from database.db import db
from datetime import datetime

class BatchState:
    HARVESTED = "Harvested"
    IN_TRANSIT = "InTransit"
    IN_COLD_STORAGE = "InColdStorage"
    DELIVERED = "Delivered"
    REJECTED = "Rejected"


class SpinachBatch(db.Model):
    __tablename__ = "spinach_batches"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(db.String(100), unique=True, nullable=False)

    ipfs_cid = db.Column(db.String(255), nullable=True)
    merkle_root = db.Column(db.String(66), nullable=True)

    farmer_address = db.Column(db.String(42), nullable=False)
    current_owner = db.Column(db.String(42), nullable=False)

    blockchain_tx_hash = db.Column(db.String(66), nullable=True)

    state = db.Column(db.String(50), default=BatchState.HARVESTED)

    cold_chain_violated = db.Column(db.Boolean, default=False)

    # 🔹 Link to Farm
    farm_id = db.Column(
        db.Integer,
        db.ForeignKey("farms.id"),
        nullable=True
    )

    # 🔹 Stage Timestamps
    harvest_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    transit_timestamp = db.Column(db.DateTime, nullable=True)
    storage_timestamp = db.Column(db.DateTime, nullable=True)
    delivery_timestamp = db.Column(db.DateTime, nullable=True)
    rejection_timestamp = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 🔹 AI Prediction Results
    predicted_yield = db.Column(db.Float, nullable=True)
    disease_probability = db.Column(db.Float, nullable=True)
    health_score = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "ipfs_cid": self.ipfs_cid,
            "merkle_root": self.merkle_root,
            "farmer_address": self.farmer_address,
            "current_owner": self.current_owner,
            "state": self.state,
            "cold_chain_violated": self.cold_chain_violated,
            "harvest_timestamp": self.harvest_timestamp.isoformat() if self.harvest_timestamp else None,
            "transit_timestamp": self.transit_timestamp.isoformat() if self.transit_timestamp else None,
            "storage_timestamp": self.storage_timestamp.isoformat() if self.storage_timestamp else None,
            "delivery_timestamp": self.delivery_timestamp.isoformat() if self.delivery_timestamp else None,
            "rejection_timestamp": self.rejection_timestamp.isoformat() if self.rejection_timestamp else None,
            "predicted_yield": self.predicted_yield,
            "disease_probability": self.disease_probability,
            "health_score": self.health_score,
            "blockchain_tx_hash": self.blockchain_tx_hash
        }