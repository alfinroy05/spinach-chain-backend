from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database.db import db
from models.batch_model import SpinachBatch
from models.sensor_model import SensorReading
from services.ai_service import run_ai_analysis

ai_bp = Blueprint("ai_bp", __name__)


# --------------------------------------------------
# 🔹 AI PREDICTION FOR A BATCH
# --------------------------------------------------
@ai_bp.route("/predict/<batch_id>", methods=["GET"])
@jwt_required()
def predict_batch(batch_id):
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

        # 🔹 Run AI service safely
        try:
            ai_result = run_ai_analysis(sensor_data)
        except Exception as ai_error:
            return jsonify({
                "error": "AI processing failed",
                "details": str(ai_error)
            }), 500

        # 🔹 Store AI results (if columns exist)
        if hasattr(batch, "predicted_yield"):
            batch.predicted_yield = ai_result.get("predicted_yield")

        if hasattr(batch, "disease_probability"):
            batch.disease_probability = ai_result.get("disease_probability")

        if hasattr(batch, "health_score"):
            batch.health_score = ai_result.get("health_score")

        db.session.commit()

        return jsonify({
            "batch_id": batch_id,
            "predicted_yield": ai_result.get("predicted_yield"),
            "disease_probability": ai_result.get("disease_probability"),
            "health_score": ai_result.get("health_score"),
            "anomaly_detected": ai_result.get("anomaly_detected")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500