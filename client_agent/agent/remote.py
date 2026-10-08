"""Agent-side handling of remote desktop session requests.

This module does NOT create a covert remote-control protocol.
It polls the server for authorized session requests, acknowledges them,
and optionally launches the legitimate Windows Remote Desktop client
(mstsc.exe) as a visual demonstration.
"""

import platform
import subprocess

import requests

from agent.config import Config


def poll_pending_session(token: str):
    """GET /api/client/pending-session. Returns session dict or None."""
    url = f"{Config.SERVER_URL}/api/client/pending-session"
    headers = {"X-Device-Token": token}
    try:
        resp = requests.get(url, headers=headers, timeout=Config.HTTP_TIMEOUT)
    except requests.RequestException as exc:
        print(f"[remote] poll error: {exc}")
        return None

    if resp.status_code != 200:
        return None

    return resp.json().get("data")


def report_session_status(token: str, session_id: int, status: str) -> bool:
    """POST /api/client/session-status."""
    url = f"{Config.SERVER_URL}/api/client/session-status"
    headers = {"X-Device-Token": token}
    payload = {"session_id": session_id, "status": status}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=Config.HTTP_TIMEOUT)
    except requests.RequestException as exc:
        print(f"[remote] report error: {exc}")
        return False

    if resp.status_code != 200:
        print(f"[remote] report failed: {resp.status_code} {resp.text}")
        return False
    return True


def launch_remote_desktop(target: str = "") -> bool:
    """Launch the legitimate Windows Remote Desktop client.

    Only runs on Windows. On other OSes returns False.
    This just opens mstsc.exe — a normal Windows program. It does NOT
    create any remote-control channel or bypass authentication.
    """
    if platform.system() != "Windows":
        return False

    cmd = ["mstsc"]
    if target:
        cmd.append(f"/v:{target}")

    try:
        subprocess.Popen(cmd, shell=False)
        print(f"[remote] launched mstsc (target={target or 'none'})")
        return True
    except Exception as exc:
        print(f"[remote] failed to launch mstsc: {exc}")
        return False