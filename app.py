import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.db import init_db

# ✅ Import global extensions (NO circular import)
from extensions import bcrypt, jwt

# 🔹 Import Blueprints
from routes.sensor_routes import sensor_bp
from routes.batch_routes import batch_bp
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp

# 🔹 Import Models (important for db.create_all)
from models.batch_model import SpinachBatch
from models.user_model import User
from models.farm_model import Farm


def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔹 Load Configuration
    # --------------------------------------------------
    app.config.from_object(Config)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 24  # 24 hours

    # --------------------------------------------------
    # 🔹 Configure Logging
    # --------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("🚀 Starting SpinachChain Backend...")

    # --------------------------------------------------
    # 🔹 Enable CORS
    # --------------------------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True
    )

    # --------------------------------------------------
    # 🔹 Initialize Extensions (CORRECT WAY)
    # --------------------------------------------------
    bcrypt.init_app(app)
    jwt.init_app(app)

    # --------------------------------------------------
    # 🔹 Initialize Database
    # --------------------------------------------------
    try:
        init_db(app)
        logging.info("✅ Database initialized successfully")
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        raise e

    # --------------------------------------------------
    # 🔹 Register Blueprints
    # --------------------------------------------------
    app.register_blueprint(sensor_bp, url_prefix="/api")
    app.register_blueprint(batch_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    logging.info("✅ Blueprints registered")

    # --------------------------------------------------
    # 🔹 Health Check Route
    # --------------------------------------------------
    @app.route("/")
    def health_check():
        return jsonify({
            "status": "SpinachChain Backend Running",
            "version": "Phase 2 - Auth Fixed",
            "environment": os.getenv("FLASK_ENV", "development")
        }), 200

    # --------------------------------------------------
    # 🔹 JWT Error Handlers
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
    # 🔹 404 Handler
    # --------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Route not found"}), 404

    # --------------------------------------------------
    # 🔹 Global Exception Handler
    # --------------------------------------------------
    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.error(f"🔥 Unhandled Exception: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

    return app


# --------------------------------------------------
# 🔹 Create App Instance
# --------------------------------------------------
app = create_app()


# --------------------------------------------------
# 🔹 Run App
# --------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=app.config.get("DEBUG", True)
    )