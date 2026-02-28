import logging
from datetime import timedelta
from flask import Flask, jsonify
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

# Models (important for db.create_all)
from models.batch_model import SpinachBatch
from models.user_model import User
from models.farm_model import Farm



def create_app():
    app = Flask(__name__)

    # --------------------------------------------------
    # Load Base Config
    # --------------------------------------------------
    app.config.from_object(Config)

    # --------------------------------------------------
    # 🔐 JWT CONFIGURATION (FIXED PROPERLY)
    # --------------------------------------------------
    app.config["JWT_SECRET_KEY"] = "spinachchain_super_secure_fixed_key_2026"

    # ✅ MUST use timedelta (NOT integer)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    # Explicit JWT header configuration
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("🚀 Starting SpinachChain Backend...")

    # --------------------------------------------------
    # ✅ PROPER CORS CONFIGURATION
    # --------------------------------------------------
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": "http://localhost:3000"
            }
        }
    )

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
        migrate = Migrate(app, db)
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
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
            "environment": "development"
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

    return app
    

# --------------------------------------------------
# Create App Instance
# --------------------------------------------------
app = create_app()


# --------------------------------------------------
# 🔥 RUN WITHOUT DEBUG RELOADER
# --------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )