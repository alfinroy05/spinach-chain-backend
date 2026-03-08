import logging
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from database.db import init_db

# Extensions
from extensions import bcrypt, jwt

# Blueprints
from routes.sensor_routes import sensor_bp
from routes.batch_routes import batch_bp
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp

# 🔥 AI SERVICE (Preload models once)
from services.ai_service import load_models


# ======================================================
# 🔥 CREATE APP FACTORY
# ======================================================

def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # Load Base Config
    # --------------------------------------------------
    app.config.from_object(Config)

    # --------------------------------------------------
    # 🔐 JWT CONFIGURATION
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = "spinachchain_super_secure_fixed_key_2026"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    # --------------------------------------------------
    # 🔥 IMAGE UPLOAD LIMIT (Important for AI)
    # --------------------------------------------------
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB limit

    # --------------------------------------------------
    # Logging Configuration
    # --------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("🚀 Starting SpinachChain Backend...")

    # --------------------------------------------------
    # ✅ GLOBAL CORS CONFIG
    # --------------------------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:3000"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=True
    )

    # --------------------------------------------------
    # 🔥 Allow OPTIONS to bypass JWT
    # --------------------------------------------------
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return app.make_default_options_response()

    # --------------------------------------------------
    # Initialize Extensions
    # --------------------------------------------------
    bcrypt.init_app(app)
    jwt.init_app(app)

    # --------------------------------------------------
    # Initialize Database
    # --------------------------------------------------
    try:
        init_db(app)
        logging.info("✅ Database initialized successfully")

        from flask_migrate import Migrate
        from database.db import db
        Migrate(app, db)

    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        raise e

    # --------------------------------------------------
    # 🔥 PRELOAD AI MODELS (Only Once)
    # --------------------------------------------------
    try:
        load_models()
        logging.info("✅ AI Models Loaded Successfully")
    except Exception as e:
        logging.error(f"❌ AI Model Loading Failed: {e}")
        raise e

    # --------------------------------------------------
    # Register Blueprints
    # --------------------------------------------------
    app.register_blueprint(sensor_bp, url_prefix="/api")
    app.register_blueprint(batch_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    logging.info("✅ Blueprints registered")

    # --------------------------------------------------
    # Health Check
    # --------------------------------------------------
    @app.route("/")
    def health_check():
        return jsonify({
            "status": "SpinachChain Backend Running",
            "environment": "development",
            "ai_loaded": True
        }), 200

    # --------------------------------------------------
    # JWT Error Handlers
    # --------------------------------------------------
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"error": "Authorization header missing"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token expired"}), 401

    # --------------------------------------------------
    # Global Error Handler
    # --------------------------------------------------
    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "Uploaded file too large"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        logging.error(f"Internal Server Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return app


# ======================================================
# 🔥 CREATE APP INSTANCE
# ======================================================

app = create_app()


# ======================================================
# 🚀 RUN SERVER
# ======================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )