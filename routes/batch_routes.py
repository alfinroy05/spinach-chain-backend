from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.batch_model import SpinachBatch, BatchState
from models.sensor_model import SensorReading
from services.merkle_service import generate_merkle_root
from services.ipfs_service import upload_to_ipfs
from utils.hash_utils import hash_sensor_reading

batch_bp = Blueprint("batch_bp", __name__)


# --------------------------------------------------
# 🔹 CREATE BATCH (Farmer Only)
# --------------------------------------------------
@batch_bp.route("/create-batch", methods=["POST"])
@jwt_required()
def create_batch():
    try:
        user = get_jwt_identity()

        if user["role"] != "farmer":
            return jsonify({"error": "Only farmers can create batches"}), 403

        data = request.json
        batch_id = data.get("batch_id")

        if not batch_id:
            return jsonify({"error": "Missing batch_id"}), 400

        existing = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if existing:
            return jsonify({"error": "Batch already exists"}), 400

        new_batch = SpinachBatch(
            batch_id=batch_id,
            farmer_address=user["username"],  # wallet can be linked later
            current_owner=user["username"],
            state=BatchState.HARVESTED
        )

        db.session.add(new_batch)
        db.session.commit()

        return jsonify({
            "message": "Batch created successfully",
            "batch": new_batch.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# 🔹 ADD SENSOR DATA (Farmer Only)
# --------------------------------------------------
@batch_bp.route("/add-sensor/<batch_id>", methods=["POST"])
@jwt_required()
def add_sensor_reading(batch_id):
    try:
        user = get_jwt_identity()

        if user["role"] != "farmer":
            return jsonify({"error": "Only farmers can add sensor data"}), 403

        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        if batch.current_owner != user["username"]:
            return jsonify({"error": "Not batch owner"}), 403

        data = request.json

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


# --------------------------------------------------
# 🔹 FINALIZE BATCH (Farmer Only)
# --------------------------------------------------
@batch_bp.route("/finalize-batch/<batch_id>", methods=["POST"])
@jwt_required()
def finalize_batch(batch_id):
    try:
        user = get_jwt_identity()

        if user["role"] != "farmer":
            return jsonify({"error": "Only farmers can finalize batches"}), 403

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
            "farmer": batch.farmer_address,
            "sensor_readings": [r.to_dict() for r in readings],
            "merkle_root": merkle_root
        }

        ipfs_cid = upload_to_ipfs(batch_payload)

        batch.merkle_root = merkle_root
        batch.ipfs_cid = ipfs_cid

        db.session.commit()

        return jsonify({
            "message": "Batch finalized - Ready for blockchain",
            "merkle_root": merkle_root,
            "ipfs_cid": ipfs_cid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# 🔹 UPDATE STAGE (Current Owner Only)
# --------------------------------------------------
@batch_bp.route("/update-stage/<batch_id>", methods=["POST"])
@jwt_required()
def update_stage(batch_id):
    try:
        user = get_jwt_identity()
        data = request.json
        new_state = data.get("state")

        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        if batch.current_owner != user["username"]:
            return jsonify({"error": "Not batch owner"}), 403

        batch.state = new_state
        batch.current_owner = data.get("new_owner")

        db.session.commit()

        return jsonify({
            "message": "Batch updated successfully",
            "batch": batch.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# 🔹 GET ALL BATCHES (Authenticated Users)
# --------------------------------------------------
@batch_bp.route("/batches", methods=["GET"])
@jwt_required()
def get_all_batches():
    try:
        batches = SpinachBatch.query.all()
        return jsonify({
            "batches": [b.to_dict() for b in batches]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500