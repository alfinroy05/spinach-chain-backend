from database.db import db
from datetime import datetime


class SpinachBatch(db.Model):
    __tablename__ = "spinach_batches"

    id = db.Column(db.Integer, primary_key=True)

    # 🔹 Unique Batch Identifier (Same as Blockchain ID)
    batch_id = db.Column(db.String(100), unique=True, nullable=False)

    # 🔹 Off-chain Integrity Data
    ipfs_cid = db.Column(db.String(255), nullable=True)
    merkle_root = db.Column(db.String(66), nullable=True)

    # 🔹 Optional: Store blockchain tx hash for reference
    blockchain_tx_hash = db.Column(db.String(66), nullable=True)

    # 🔹 Link to Farm (Optional Off-chain metadata)
    farm_id = db.Column(
        db.Integer,
        db.ForeignKey("farms.id"),
        nullable=True
    )

    # 🔹 Off-chain timestamps
    harvest_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ======================================================
    # 🔥 AI Prediction Results (Fully Synced With AI ROUTE)
    # ======================================================

    environmental_risk = db.Column(db.Float, nullable=True)
    disease_probability = db.Column(db.Float, nullable=True)
    health_score = db.Column(db.Float, nullable=True)
    anomaly_detected = db.Column(db.Boolean, nullable=True)
    disease_class = db.Column(db.String(255), nullable=True)
    predicted_yield = db.Column(db.Float, nullable=True)

    # ======================================================
    # 🔹 SAFE SERIALIZER
    # ======================================================

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "ipfs_cid": self.ipfs_cid,
            "merkle_root": self.merkle_root,
            "blockchain_tx_hash": self.blockchain_tx_hash,
            "harvest_timestamp": self.harvest_timestamp.isoformat() if self.harvest_timestamp else None,

            # AI Fields (Safe JSON Conversion)
            "environmental_risk": float(self.environmental_risk) if self.environmental_risk is not None else 0,
            "disease_probability": float(self.disease_probability) if self.disease_probability is not None else 0,
            "health_score": float(self.health_score) if self.health_score is not None else 0,
            "anomaly_detected": bool(self.anomaly_detected) if self.anomaly_detected is not None else False,
            "disease_class": self.disease_class if self.disease_class else None,
            "predicted_yield": float(self.predicted_yield) if self.predicted_yield is not None else 0
        }

    def __repr__(self):
        return f"<SpinachBatch {self.batch_id}>"