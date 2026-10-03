import platform
import socket
import uuid


def get_hostname() -> str:
    return socket.gethostname()


def get_ip_address() -> str:
    """Best-effort local IP (works without internet)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_mac_address() -> str:
    mac_num = uuid.getnode()
    mac_hex = f"{mac_num:012x}"
    mac = ":".join(mac_hex[i:i + 2] for i in range(0, 12, 2)).upper()
    return mac


def get_operating_system() -> str:
    return f"{platform.system()} {platform.release()} ({platform.version()})"