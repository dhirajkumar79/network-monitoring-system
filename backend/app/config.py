import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    HEARTBEAT_TIMEOUT_SECONDS = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "60"))

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Cloud Database SSL (for Aiven) ---
    # If we are using a cloud database, require the ca.pem file.
    # If we are testing locally, skip the SSL.
    if "aivencloud.com" in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl": {
                    "ca": "ca.pem"  # Path to the cert you downloaded
                }
            }
        }

    # --- JWT ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)