from flask import Blueprint, request, jsonify
from database.db import db
from models.sensor_model import SensorReading
from models.batch_model import SpinachBatch
from utils.hash_utils import hash_sensor_reading
from datetime import datetime

sensor_bp = Blueprint("sensor_bp", __name__)


# =====================================================
# ADD SENSOR DATA (ESP32 / IoT DEVICE)
# =====================================================
@sensor_bp.route("/sensor-data/<batch_id>", methods=["POST"])
def receive_sensor_data(batch_id):
    try:
        # Find batch using business ID
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()

        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        # Parse JSON safely
        data = request.get_json(force=True)

        print("Incoming sensor payload:", data)

        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Validate required fields
        required_fields = ["N", "P", "K", "temperature", "humidity"]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        # Convert values safely
        nitrogen = float(data["N"])
        phosphorus = float(data["P"])
        potassium = float(data["K"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        # Generate integrity hash
        data_hash = hash_sensor_reading(data)

        # Store sensor reading
        reading = SensorReading(
            batch_id=batch.id,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            data_hash=data_hash,
            created_at=datetime.utcnow()
        )

        db.session.add(reading)
        db.session.commit()

        return jsonify({
            "message": "Sensor data stored successfully",
            "batch_id": batch.batch_id,
            "data_hash": data_hash
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Sensor insert error:", str(e))
        return jsonify({"error": str(e)}), 500


# =====================================================
# GET SENSOR DATA FOR A BATCH (Dashboard)
# =====================================================
@sensor_bp.route("/sensor-data/<batch_id>", methods=["GET"])
def get_sensor_data(batch_id):
    try:
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()

        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        readings = SensorReading.query.filter_by(batch_id=batch.id).all()

        return jsonify({
            "batch_id": batch.batch_id,
            "sensor_readings": [r.to_dict() for r in readings]
        }), 200

    except Exception as e:
        print("Fetch sensor error:", str(e))
        return jsonify({"error": str(e)}), 500