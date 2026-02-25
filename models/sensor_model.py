from database.db import db
from datetime import datetime


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    # 🔹 Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # 🔹 Foreign Key (Properly referencing PRIMARY KEY)
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("spinach_batches.id", ondelete="CASCADE"),
        nullable=False
    )

    # 🔹 Relationship to Batch
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
    soil_moisture = db.Column(db.Float, nullable=False)

    # -------------------------------------------------
    # 🔹 NPK readings
    # -------------------------------------------------
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)

    # -------------------------------------------------
    # 🔹 Optional advanced sensor values
    # -------------------------------------------------
    ph_level = db.Column(db.Float, nullable=True)
    light_intensity = db.Column(db.Float, nullable=True)
    cold_chain_temperature = db.Column(db.Float, nullable=True)

    # -------------------------------------------------
    # 🔹 AI flags
    # -------------------------------------------------
    anomaly_detected = db.Column(db.Boolean, default=False)
    predicted_disease = db.Column(db.String(100), nullable=True)
    health_score = db.Column(db.Float, nullable=True)

    # -------------------------------------------------
    # 🔹 Data integrity
    # -------------------------------------------------
    data_hash = db.Column(db.String(66), nullable=True)  # SHA256 hash

    # -------------------------------------------------
    # 🔹 Timestamp
    # -------------------------------------------------
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # -------------------------------------------------
    # 🔹 Serializer
    # -------------------------------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "soil_moisture": self.soil_moisture,
            "nitrogen": self.nitrogen,
            "phosphorus": self.phosphorus,
            "potassium": self.potassium,
            "ph_level": self.ph_level,
            "light_intensity": self.light_intensity,
            "cold_chain_temperature": self.cold_chain_temperature,
            "anomaly_detected": self.anomaly_detected,
            "predicted_disease": self.predicted_disease,
            "health_score": self.health_score,
            "data_hash": self.data_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }