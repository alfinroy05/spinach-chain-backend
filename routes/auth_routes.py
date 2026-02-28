from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from models.user_model import User
from models.farm_model import Farm
from database.db import db
from extensions import bcrypt

auth_bp = Blueprint("auth", __name__)


# ==================================================
# 🔹 REGISTER USER (FULL WEB3 MODE - NO WALLET STORAGE)
# ==================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        # -------- VALIDATION --------
        if not all([username, email, password, role]):
            return jsonify({
                "error": "All fields are required"
            }), 400

        # -------- CHECK DUPLICATES --------
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            return jsonify({
                "error": "Username or Email already exists"
            }), 409

        # -------- HASH PASSWORD --------
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        # -------- CREATE USER --------
        user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        # -------- CREATE FARM PROFILE IF FARMER --------
        if role == "farmer":
            farm = Farm(
                farmer_id=user.id,
                farm_name=data.get("farm_name", "Unnamed Farm"),
                location=data.get("location", "Unknown"),
                organic_certified=data.get("organic_certified", False)
            )
            db.session.add(farm)
            db.session.commit()

        return jsonify({
            "message": "User registered successfully",
            "role": role
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================================================
# 🔹 LOGIN USER (JWT SESSION ONLY)
# ==================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "error": "Username and password required"
            }), 400

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        # -------- JWT IDENTITY = user.id ONLY --------
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "role": user.role,
            "user_id": user.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500