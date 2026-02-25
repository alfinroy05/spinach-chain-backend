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

    # 🔹 Unique batch ID (matches blockchain batchId)
    batch_id = db.Column(db.String(100), unique=True, nullable=False)

    # 🔹 IPFS content identifier
    ipfs_cid = db.Column(db.String(255), nullable=True)

    # 🔹 Merkle root stored on-chain
    merkle_root = db.Column(db.String(66), nullable=True)  # 0x + 64 hex chars

    # 🔹 Wallet addresses
    farmer_address = db.Column(db.String(42), nullable=False)
    current_owner = db.Column(db.String(42), nullable=False)

    # 🔹 Blockchain transaction hash
    blockchain_tx_hash = db.Column(db.String(66), nullable=True)

    # 🔹 Batch lifecycle state
    state = db.Column(
        db.String(50),
        default=BatchState.HARVESTED
    )

    # 🔹 Cold chain violation flag
    cold_chain_violated = db.Column(
        db.Boolean,
        default=False
    )

    # 🔹 Timestamps
    harvest_timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

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
            "predicted_yield": self.predicted_yield,
            "disease_probability": self.disease_probability,
            "health_score": self.health_score,
            "blockchain_tx_hash": self.blockchain_tx_hash
        }