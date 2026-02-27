from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from models.user_model import User
from database.db import db
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hashed_pw,
        role=data["role"]
    )

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully"}