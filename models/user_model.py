from database.db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    # ================= PRIMARY INFO =================
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # ================= ROLE =================
    role = db.Column(
        db.String(50),
        nullable=False
    )

    # ================= META =================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ================= HELPER METHODS =================
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"