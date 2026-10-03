from typing import Optional

import requests

from agent import network
from agent.config import Config, TOKEN_FILE


def load_token() -> Optional[str]:
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        return token or None
    return None


def save_token(token: str) -> None:
    TOKEN_FILE.write_text(token, encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except Exception:
        pass


def register() -> Optional[str]:
    """Contact the server and register this device."""
    device_name = Config.DEVICE_NAME or network.get_hostname()

    payload = {
        "device_name": device_name,
        "hostname": network.get_hostname(),
        "operating_system": network.get_operating_system(),
        "ip_address": network.get_ip_address(),
        "mac_address": network.get_mac_address(),
        "location": Config.LOCATION,
    }

    url = f"{Config.SERVER_URL}/api/client/register"
    try:
        resp = requests.post(url, json=payload, timeout=Config.HTTP_TIMEOUT)
    except requests.RequestException as exc:
        print(f"[register] Could not reach server: {exc}")
        return None

    if resp.status_code != 201:
        print(f"[register] Server returned {resp.status_code}: {resp.text}")
        return None

    data = resp.json().get("data", {})
    token = data.get("device_token")
    if not token:
        print("[register] No device_token in server response.")
        return None

    save_token(token)
    print(f"[register] Registered as device_id={data.get('device_id')}")
    return token


def ensure_registered() -> Optional[str]:
    token = load_token()
    if token:
        return token
    return register()