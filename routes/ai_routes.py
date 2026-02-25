from flask import Blueprint, jsonify, request
from database.db import db
from models.batch_model import SpinachBatch
from models.sensor_model import SensorReading
from services.ai_service import run_ai_analysis

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/analyze-batch/<batch_id>", methods=["GET"])
def analyze_batch(batch_id):
    try:
        # 🔹 Fetch batch
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()

        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        # 🔹 Fetch sensor readings
        readings = SensorReading.query.filter_by(batch_id=batch_id).all()

        if not readings:
            return jsonify({"error": "No sensor data found"}), 404

        # 🔹 Convert to list of dict
        sensor_data = [r.to_dict() for r in readings]

        # 🔹 Run AI service
        ai_result = run_ai_analysis(sensor_data)

        # 🔹 Store AI results in batch
        batch.predicted_yield = ai_result["predicted_yield"]
        batch.disease_probability = ai_result["disease_probability"]
        batch.health_score = ai_result["health_score"]

        db.session.commit()

        return jsonify({
            "batch_id": batch_id,
            "predicted_yield": batch.predicted_yield,
            "disease_probability": batch.disease_probability,
            "health_score": batch.health_score,
            "anomaly_detected": ai_result["anomaly_detected"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500