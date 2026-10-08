import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Base folder of the agent
BASE_DIR = Path(__file__).resolve().parent.parent

# Where we store the assigned device token
TOKEN_FILE = BASE_DIR / "device_token.txt"


class Config:
    # Flask server URL (no trailing slash)
    SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:5000")

    # How often to send a heartbeat (seconds)
    HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))

    # HTTP request timeout (seconds)
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "10"))

    # Optional location label
    LOCATION = os.getenv("LOCATION", "Default")

    # User-facing device name (defaults to hostname if blank)
    DEVICE_NAME = os.getenv("DEVICE_NAME", "")

    # Target for Remote Desktop demo (blank = just open mstsc)
    REMOTE_DESKTOP_TARGET = os.getenv("REMOTE_DESKTOP_TARGET", "")