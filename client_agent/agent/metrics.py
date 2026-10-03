import time

import psutil


def _get_network_totals():
    io = psutil.net_io_counters()
    return io.bytes_sent, io.bytes_recv


_last = {
    "time": None,
    "sent": 0,
    "recv": 0,
}


def collect_metrics() -> dict:
    """Return current system metrics. Network values are rates (bytes/sec)."""
    global _last

    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent

    try:
        disk = psutil.disk_usage("/").percent
    except Exception:
        disk = psutil.disk_usage("C:\\").percent

    sent, recv = _get_network_totals()
    now = time.time()

    if _last["time"] is None:
        up_rate = 0.0
        down_rate = 0.0
    else:
        elapsed = max(now - _last["time"], 0.001)
        up_rate = max(sent - _last["sent"], 0) / elapsed
        down_rate = max(recv - _last["recv"], 0) / elapsed

    _last = {"time": now, "sent": sent, "recv": recv}

    return {
        "cpu_usage": round(cpu, 2),
        "memory_usage": round(memory, 2),
        "disk_usage": round(disk, 2),
        "network_upload": round(up_rate, 2),
        "network_download": round(down_rate, 2),
    }


def measure_latency(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0):
    """Approximate latency by timing a TCP connect. Returns ms or None."""
    import socket

    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed = (time.time() - start) * 1000
        return round(elapsed, 2)
    except Exception:
        return None