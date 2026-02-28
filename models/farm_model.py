from database.db import db
from datetime import datetime

class Farm(db.Model):
    __tablename__ = "farms"

    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    farm_name = db.Column(db.String(200))
    location = db.Column(db.String(200))
    organic_certified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)