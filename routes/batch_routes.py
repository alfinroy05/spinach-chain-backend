from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.batch_model import SpinachBatch
from models.sensor_model import SensorReading
from models.user_model import User
from services.merkle_service import generate_merkle_root
from services.ipfs_service import upload_to_ipfs
from utils.hash_utils import hash_sensor_reading

batch_bp = Blueprint("batch_bp", __name__)


# ==================================================
# 🔹 Helper: Get Current Logged-In User
# ==================================================
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        return User.query.get(user_id)
    except:
        return None


# ==================================================
# 🔹 CREATE BATCH (OFF-CHAIN METADATA ONLY)
# ==================================================
@batch_bp.route("/create-batch", methods=["POST"])
@jwt_required()
def create_batch():
    try:
        user = get_current_user()

        if not user or user.role != "farmer":
            return jsonify({"error": "Only farmers can create batches"}), 403

        data = request.get_json() or {}
        batch_id = data.get("batch_id")

        if not batch_id:
            return jsonify({"error": "Missing batch_id"}), 400

        existing = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if existing:
            return jsonify({"error": "Batch already exists"}), 400

        new_batch = SpinachBatch(
            batch_id=batch_id
        )

        db.session.add(new_batch)
        db.session.commit()

        return jsonify({
            "message": "Batch metadata created (create on blockchain next)",
            "batch": new_batch.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 GET ALL BATCHES (ROLE BASED ACCESS ONLY)
# ==================================================
@batch_bp.route("/batches", methods=["GET"])
@jwt_required()
def get_all_batches():
    try:
        batches = SpinachBatch.query.all()
        return jsonify([b.to_dict() for b in batches]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 GET SINGLE BATCH (OFF-CHAIN DATA ONLY)
# ==================================================
@batch_bp.route("/batch/<batch_id>", methods=["GET"])
@jwt_required()
def get_batch(batch_id):
    try:
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()

        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        return jsonify(batch.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 GET SENSOR DATA
# ==================================================
@batch_bp.route("/sensor-data/<batch_id>", methods=["GET"])
@jwt_required()
def get_sensor_data(batch_id):
    try:
        readings = SensorReading.query.filter_by(batch_id=batch_id).all()
        return jsonify([r.to_dict() for r in readings]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 ADD SENSOR DATA (NO OWNER CHECK HERE)
# ==================================================
@batch_bp.route("/add-sensor/<batch_id>", methods=["POST"])
@jwt_required()
def add_sensor_reading(batch_id):
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        data = request.get_json() or {}
        data_hash = hash_sensor_reading(data)

        reading = SensorReading(
            batch_id=batch_id,
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            soil_moisture=data.get("soil_moisture"),
            nitrogen=data.get("nitrogen"),
            phosphorus=data.get("phosphorus"),
            potassium=data.get("potassium"),
            ph_level=data.get("ph_level"),
            light_intensity=data.get("light_intensity"),
            cold_chain_temperature=data.get("cold_chain_temperature"),
            data_hash=data_hash
        )

        db.session.add(reading)
        db.session.commit()

        return jsonify({
            "message": "Sensor reading added",
            "data_hash": data_hash
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 FINALIZE BATCH (GENERATE IPFS + MERKLE)
# ==================================================
@batch_bp.route("/finalize-batch/<batch_id>", methods=["POST"])
@jwt_required()
def finalize_batch(batch_id):
    try:
        user = get_current_user()

        if not user or user.role != "farmer":
            return jsonify({"error": "Unauthorized"}), 403

        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        readings = SensorReading.query.filter_by(batch_id=batch_id).all()
        if not readings:
            return jsonify({"error": "No sensor data found"}), 400

        hashes = [r.data_hash for r in readings if r.data_hash]
        merkle_root = generate_merkle_root(hashes)

        batch_payload = {
            "batch_id": batch.batch_id,
            "sensor_readings": [r.to_dict() for r in readings],
            "merkle_root": merkle_root
        }

        ipfs_cid = upload_to_ipfs(batch_payload)

        batch.merkle_root = merkle_root
        batch.ipfs_cid = ipfs_cid

        db.session.commit()

        return jsonify({
            "message": "Batch finalized - now call createBatch() on blockchain",
            "merkle_root": merkle_root,
            "ipfs_cid": ipfs_cid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500