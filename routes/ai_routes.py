from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from database.db import db
from models.batch_model import SpinachBatch
from models.sensor_model import SensorReading
from services.ipfs_service import upload_json_to_ipfs
from services.merkle_service import generate_merkle_root
import os

ai_bp = Blueprint("ai_bp", __name__)

# ======================================================
# 🔥 ENV CHECK
# ======================================================
ENV = os.getenv("FLASK_ENV", "production")

# ======================================================
# 🔥 CONDITIONAL AI IMPORT (IMPORTANT FIX)
# ======================================================
if ENV != "production":
    from services.ai_service import run_ai_analysis, generate_metadata
else:
    # Dummy AI functions for production
    def run_ai_analysis(sensor_data, image_file):
        return {
            "environmental_risk": 0,
            "disease_probability": 0,
            "health_score": 50,
            "anomaly_detected": False,
            "disease_class": "Unknown (AI disabled)"
        }

    def generate_metadata(batch, ai_result):
        return {
            "batch_id": batch.batch_id,
            "ai_enabled": False,
            "note": "AI disabled in production"
        }


# ======================================================
# 🔥 AI + IPFS + MERKLE PIPELINE
# ======================================================
@ai_bp.route("/predict/<batch_id>", methods=["POST"])
@jwt_required()
def predict_batch(batch_id):

    try:
        current_user = get_jwt_identity()

        # --------------------------------------------------
        # 🔹 Fetch Batch
        # --------------------------------------------------
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        # --------------------------------------------------
        # 🔹 Fetch Sensor Data
        # --------------------------------------------------
        readings = SensorReading.query.filter_by(batch_id=batch.id).all()
        if not readings:
            return jsonify({"error": "No sensor data found"}), 404

        sensor_data = [r.to_dict() for r in readings]

        # --------------------------------------------------
        # 🔹 Image handling
        # --------------------------------------------------
        image_file = request.files.get("image")

        # In production → skip image requirement
        if ENV != "production" and not image_file:
            return jsonify({"error": "Image file is required"}), 400

        # --------------------------------------------------
        # 🔥 AI ANALYSIS (SAFE)
        # --------------------------------------------------
        try:
            ai_result = run_ai_analysis(sensor_data, image_file)
        except Exception as ai_error:
            return jsonify({
                "error": "AI processing failed",
                "details": str(ai_error)
            }), 500

        # --------------------------------------------------
        # 🔹 Update DB
        # --------------------------------------------------
        try:
            batch.environmental_risk = ai_result.get("environmental_risk")
            batch.disease_probability = ai_result.get("disease_probability")
            batch.health_score = ai_result.get("health_score")
            batch.anomaly_detected = ai_result.get("anomaly_detected")
            batch.disease_class = ai_result.get("disease_class")

            db.session.commit()

        except Exception as db_error:
            db.session.rollback()
            return jsonify({
                "error": "Database update failed",
                "details": str(db_error)
            }), 500

        # --------------------------------------------------
        # 🌳 MERKLE ROOT
        # --------------------------------------------------
        try:
            hashes = [r.data_hash for r in readings if r.data_hash]
            merkle_root = generate_merkle_root(hashes)
        except Exception as merkle_error:
            return jsonify({
                "error": "Merkle root failed",
                "details": str(merkle_error)
            }), 500

        # --------------------------------------------------
        # 🔥 IPFS METADATA
        # --------------------------------------------------
        try:
            metadata = generate_metadata(batch, ai_result)
            metadata["merkle_root"] = merkle_root
            metadata["sensor_readings"] = sensor_data

            cid = upload_json_to_ipfs(metadata)
        except Exception as ipfs_error:
            return jsonify({
                "error": "IPFS upload failed",
                "details": str(ipfs_error)
            }), 500

        # --------------------------------------------------
        # 🔹 SAVE CID + MERKLE
        # --------------------------------------------------
        try:
            batch.ipfs_cid = cid
            batch.merkle_root = merkle_root
            db.session.commit()
        except Exception as save_error:
            db.session.rollback()
            return jsonify({
                "error": "Save failed",
                "details": str(save_error)
            }), 500

        # --------------------------------------------------
        # 🔥 RESPONSE
        # --------------------------------------------------
        return jsonify({
            "batch_id": str(batch.batch_id),
            "ipfs_cid": str(cid),
            "merkle_root": str(merkle_root),
            "ai_analysis": {
                "environmental_risk": float(ai_result.get("environmental_risk", 0)),
                "disease_probability": float(ai_result.get("disease_probability", 0)),
                "health_score": float(ai_result.get("health_score", 0)),
                "anomaly_detected": bool(ai_result.get("anomaly_detected", False)),
                "disease_class": ai_result.get("disease_class")
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🔎 GET AI RESULTS
# ======================================================
@ai_bp.route("/ai/analyze-batch/<batch_id>", methods=["GET"])
@jwt_required()
def analyze_batch(batch_id):
    try:
        batch = SpinachBatch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        return jsonify({
            "batch_id": str(batch.batch_id),
            "environmental_risk": float(batch.environmental_risk or 0),
            "disease_probability": float(batch.disease_probability or 0),
            "health_score": float(batch.health_score or 0),
            "anomaly_detected": bool(batch.anomaly_detected) if batch.anomaly_detected is not None else False,
            "disease_class": batch.disease_class
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500