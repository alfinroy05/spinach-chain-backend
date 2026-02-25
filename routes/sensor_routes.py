from flask import Blueprint, request, jsonify
from database.db import db
from models.sensor_model import SensorReading
from models.batch_model import SpinachBatch
from utils.hash_utils import hash_sensor_reading
from datetime import datetime

sensor_bp = Blueprint("sensor_bp", __name__)


# 🔹 ESP32 Sensor Data Endpoint
@sensor_bp.route("/sensor-data/<batch_id>", methods=["POST"])
def receive_sensor_data(batch_id):
    try:
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()

        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        data = request.json

        # 🔹 Validate required fields
        required_fields = [
            "temperature",
            "humidity",
            "soil_moisture",
            "nitrogen",
            "phosphorus",
            "potassium"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        # 🔹 Generate SHA256 integrity hash
        data_hash = hash_sensor_reading(data)

        reading = SensorReading(
            batch_id=batch_id,
            temperature=data["temperature"],
            humidity=data["humidity"],
            soil_moisture=data["soil_moisture"],
            nitrogen=data["nitrogen"],
            phosphorus=data["phosphorus"],
            potassium=data["potassium"],
            ph_level=data.get("ph_level"),
            light_intensity=data.get("light_intensity"),
            cold_chain_temperature=data.get("cold_chain_temperature"),
            data_hash=data_hash,
            created_at=datetime.utcnow()
        )

        db.session.add(reading)
        db.session.commit()

        return jsonify({
            "message": "Sensor data stored successfully",
            "batch_id": batch_id,
            "data_hash": data_hash
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Get All Sensor Data for a Batch
@sensor_bp.route("/sensor-data/<batch_id>", methods=["GET"])
def get_sensor_data(batch_id):
    try:
        readings = SensorReading.query.filter_by(batch_id=batch_id).all()

        if not readings:
            return jsonify({"message": "No sensor data found"}), 404

        return jsonify({
            "batch_id": batch_id,
            "sensor_readings": [r.to_dict() for r in readings]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500