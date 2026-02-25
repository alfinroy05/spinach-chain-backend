from flask import Blueprint, request, jsonify
from database.db import db
from models.batch_model import SpinachBatch, BatchState
from models.sensor_model import SensorReading
from services.merkle_service import generate_merkle_root
from services.ipfs_service import upload_to_ipfs
from utils.hash_utils import hash_sensor_reading


batch_bp = Blueprint("batch_bp", __name__)

# 🔹 Create Batch (DB only)
@batch_bp.route("/create-batch", methods=["POST"])
def create_batch():
    try:
        data = request.json

        batch_id = data.get("batch_id")
        farmer_address = data.get("farmer_address")

        if not batch_id or not farmer_address:
            return jsonify({"error": "Missing required fields"}), 400

        existing = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if existing:
            return jsonify({"error": "Batch already exists"}), 400

        new_batch = SpinachBatch(
            batch_id=batch_id,
            farmer_address=farmer_address,
            current_owner=farmer_address,
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


# 🔹 Add Sensor Reading
@batch_bp.route("/add-sensor/<batch_id>", methods=["POST"])
def add_sensor_reading(batch_id):
    try:
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        data = request.json

        # 🔹 Generate hash for data integrity
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


# 🔹 Finalize Batch (Generate Merkle + Upload IPFS)
@batch_bp.route("/finalize-batch/<batch_id>", methods=["POST"])
def finalize_batch(batch_id):
    try:
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        readings = SensorReading.query.filter_by(batch_id=batch_id).all()
        if not readings:
            return jsonify({"error": "No sensor data found"}), 400

        # 🔹 Collect hashes
        hashes = [r.data_hash for r in readings if r.data_hash]

        # 🔹 Generate Merkle root
        merkle_root = generate_merkle_root(hashes)

        # 🔹 Create IPFS payload
        batch_payload = {
            "batch_id": batch.batch_id,
            "farmer": batch.farmer_address,
            "sensor_readings": [r.to_dict() for r in readings],
            "merkle_root": merkle_root
        }

        # 🔹 Upload to IPFS
        ipfs_cid = upload_to_ipfs(batch_payload)

        # 🔹 Update DB (NO blockchain here)
        batch.merkle_root = merkle_root
        batch.ipfs_cid = ipfs_cid

        db.session.commit()

        return jsonify({
            "message": "Batch finalized - Ready for blockchain signing",
            "batch_id": batch.batch_id,
            "merkle_root": merkle_root,
            "ipfs_cid": ipfs_cid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Get All Batches
@batch_bp.route("/batches", methods=["GET"])
def get_all_batches():
    try:
        batches = SpinachBatch.query.all()
        return jsonify({
            "batches": [b.to_dict() for b in batches]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500