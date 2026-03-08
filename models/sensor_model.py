from database.db import db
from datetime import datetime


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    # -------------------------------------------------
    # 🔹 Primary Key
    # -------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)

    # -------------------------------------------------
    # 🔹 Foreign Key (Integer reference to SpinachBatch.id)
    # -------------------------------------------------
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("spinach_batches.id", ondelete="CASCADE"),
        nullable=False
    )

    # -------------------------------------------------
    # 🔹 Relationship
    # -------------------------------------------------
    batch = db.relationship(
        "SpinachBatch",
        backref=db.backref(
            "sensor_readings",
            cascade="all, delete-orphan",
            lazy=True
        )
    )

    # -------------------------------------------------
    # 🔹 Environmental readings
    # -------------------------------------------------
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    # -------------------------------------------------
    # 🔹 NPK readings
    # -------------------------------------------------
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)

    # -------------------------------------------------
    # 🔹 AI Outputs (Optional per reading)
    # -------------------------------------------------
    anomaly_detected = db.Column(db.Boolean, default=False)
    predicted_disease = db.Column(db.String(100), nullable=True)
    health_score = db.Column(db.Float, nullable=True)

    # -------------------------------------------------
    # 🔹 Data Integrity
    # -------------------------------------------------
    data_hash = db.Column(db.String(66), nullable=False)  # SHA256 hash

    # -------------------------------------------------
    # 🔹 Timestamp
    # -------------------------------------------------
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # -------------------------------------------------
    # 🔹 Serializer (MATCHES AI SERVICE KEYS)
    # -------------------------------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "temperature": float(self.temperature),
            "humidity": float(self.humidity),
            "nitrogen": float(self.nitrogen),
            "phosphorus": float(self.phosphorus),
            "potassium": float(self.potassium),
            "anomaly_detected": bool(self.anomaly_detected),
            "predicted_disease": self.predicted_disease,
            "health_score": float(self.health_score) if self.health_score is not None else None,
            "data_hash": self.data_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<SensorReading BatchID={self.batch_id} Temp={self.temperature}>"