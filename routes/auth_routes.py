from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from models.user_model import User
from models.farm_model import Farm
from database.db import db
from extensions import bcrypt   # ✅ CORRECT IMPORT

auth_bp = Blueprint("auth", __name__)

# --------------------------------------------------
# 🔹 REGISTER USER
# --------------------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        if not all([username, email, password, role]):
            return jsonify({"error": "All fields are required"}), 400

        # 🔹 Check duplicate user
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return jsonify({"error": "User already exists"}), 409

        # 🔹 Hash password
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        # 🔹 If farmer → create farm profile
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


# --------------------------------------------------
# 🔹 LOGIN USER
# --------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # 🔹 Compare password
        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        # 🔹 Create JWT
        access_token = create_access_token(
            identity={
                "id": user.id,
                "username": user.username,
                "role": user.role
            },
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "role": user.role
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500