import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 🔹 General
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # 🔹 Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/spinachchain_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔹 IPFS (Pinata)
    PINATA_API_KEY = os.getenv("PINATA_API_KEY")
    PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")

    # 🔹 Blockchain
    SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

    # 🔹 Ethereum Network
    SEPOLIA_CHAIN_ID = 11155111