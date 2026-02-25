import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 🔹 Load environment variables from .env
load_dotenv()

# 🔹 Initialize SQLAlchemy
db = SQLAlchemy()

# 🔹 Secure database URL (fallback for local dev)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/spinachchain_db"
)


def init_db(app):
    """
    Initialize database with Flask app (safe setup)
    """

    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # 🔹 Create tables safely
    with app.app_context():
        db.create_all()

    print("✅ Database initialized successfully")


# -------------------------------------------------------------------
# 🔹 Optional Manual Session (Advanced Queries / Background Jobs)
# -------------------------------------------------------------------

def get_engine():
    """
    Create engine safely when needed
    (Avoid global engine to prevent startup crash)
    """
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def get_db_session():
    """
    Create new SQLAlchemy session manually
    (Use only if needed)
    """
    engine = get_engine()
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    return SessionLocal()