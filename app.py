import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.db import init_db

# 🔹 Import Blueprints
from routes.sensor_routes import sensor_bp
from routes.batch_routes import batch_bp
from routes.ai_routes import ai_bp


def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # 🔹 Load Configuration
    # --------------------------------------------------
    app.config.from_object(Config)

    # --------------------------------------------------
    # 🔹 Configure Logging
    # --------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("🚀 Starting SpinachChain Backend...")

    # --------------------------------------------------
    # 🔹 Enable CORS (Allow React Frontend)
    # --------------------------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True
    )

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

    logging.info("✅ Blueprints registered")

    # --------------------------------------------------
    # 🔹 Health Check Route
    # --------------------------------------------------
    @app.route("/")
    def health_check():
        return jsonify({
            "status": "SpinachChain Backend Running",
            "version": "Phase 2 - Stable Backend",
            "environment": os.getenv("FLASK_ENV", "development")
        }), 200

    # --------------------------------------------------
    # 🔹 404 Handler
    # --------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Route not found"
        }), 404

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