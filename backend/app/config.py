import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    HEARTBEAT_TIMEOUT_SECONDS = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "60"))
    DATABASE_URL = os.getenv("DATABASE_URL", "")
