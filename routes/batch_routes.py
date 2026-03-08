from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.batch_model import SpinachBatch
from models.sensor_model import SensorReading
from models.user_model import User
from services.merkle_service import generate_merkle_root
from services.ipfs_service import upload_to_ipfs
from services.ai_service import run_ai_analysis, generate_metadata
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

        new_batch = SpinachBatch(batch_id=batch_id)

        db.session.add(new_batch)
        db.session.commit()

        return jsonify({
            "message": "Batch metadata created",
            "batch": new_batch.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 GET ALL BATCHES
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
# 🔹 GET SINGLE BATCH
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
# 🔹 ADD SENSOR DATA
# ==================================================
@batch_bp.route("/add-sensor/<batch_id>", methods=["POST"])
@jwt_required()
def add_sensor_reading(batch_id):
    try:
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
# 🔥 FINALIZE BATCH (AI + MERKLE + IPFS)
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

        image_file = request.files.get("image")
        if not image_file:
            return jsonify({"error": "Image required for AI analysis"}), 400

        # 🔥 Convert DB sensor readings to list of dicts
        sensor_data = [r.to_dict() for r in readings]

        # 🔥 RUN AI ANALYSIS
        ai_result = run_ai_analysis(sensor_data, image_file)

        # 🔥 GENERATE MERKLE ROOT
        hashes = [r.data_hash for r in readings if r.data_hash]
        merkle_root = generate_merkle_root(hashes)

        # 🔥 BUILD METADATA (WITH AI)
        metadata = generate_metadata(batch, ai_result)
        metadata["merkle_root"] = merkle_root
        metadata["sensor_readings"] = sensor_data

        # 🔥 UPLOAD TO IPFS
        ipfs_cid = upload_to_ipfs(metadata)

        # 🔥 SAVE TO DB
        batch.merkle_root = merkle_root
        batch.ipfs_cid = ipfs_cid
        batch.health_score = ai_result["health_score"]
        batch.grade = ai_result["disease_class"]

        db.session.commit()

        return jsonify({
            "message": "Batch finalized successfully",
            "merkle_root": merkle_root,
            "ipfs_cid": ipfs_cid,
            "ai_result": ai_result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500