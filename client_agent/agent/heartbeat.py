import requests

from agent.config import Config


def send_heartbeat(token: str, metrics: dict) -> bool:
    """POST metrics to /api/client/heartbeat. Returns True on success."""
    url = f"{Config.SERVER_URL}/api/client/heartbeat"
    headers = {"X-Device-Token": token}

    try:
        resp = requests.post(
            url,
            json=metrics,
            headers=headers,
            timeout=Config.HTTP_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"[heartbeat] Network error: {exc}")
        return False

    if resp.status_code == 401:
        print("[heartbeat] Token rejected (401).")
        return False

    if resp.status_code != 200:
        print(f"[heartbeat] Server returned {resp.status_code}: {resp.text}")
        return False

    return True