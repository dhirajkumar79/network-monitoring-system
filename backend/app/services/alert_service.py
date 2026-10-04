"""Threshold-based alerting.

Each time a heartbeat arrives with metrics, evaluate_alerts() checks the
values against configured thresholds and creates an Event for any breach.
"""

from app.extensions import db
from app.models.event import Event


# --- Default thresholds (can be moved to config later) ---
THRESHOLDS = {
    "cpu_usage": 85.0,        # %
    "memory_usage": 85.0,     # %
    "disk_usage": 90.0,       # %
    "latency_ms": 200.0,      # milliseconds
}


def evaluate_alerts(device_id: int, metrics: dict) -> int:
    """Create events for any metric that crosses a threshold.

    Returns the number of events created.
    """
    created = 0

    cpu = metrics.get("cpu_usage")
    if cpu is not None and cpu > THRESHOLDS["cpu_usage"]:
        db.session.add(Event(
            device_id=device_id,
            event_type="HIGH_CPU",
            severity="HIGH",
            description=f"CPU usage {cpu}% exceeded threshold {THRESHOLDS['cpu_usage']}%",
        ))
        created += 1

    mem = metrics.get("memory_usage")
    if mem is not None and mem > THRESHOLDS["memory_usage"]:
        db.session.add(Event(
            device_id=device_id,
            event_type="HIGH_MEMORY",
            severity="HIGH",
            description=f"Memory usage {mem}% exceeded threshold {THRESHOLDS['memory_usage']}%",
        ))
        created += 1

    disk = metrics.get("disk_usage")
    if disk is not None and disk > THRESHOLDS["disk_usage"]:
        db.session.add(Event(
            device_id=device_id,
            event_type="HIGH_DISK",
            severity="MEDIUM",
            description=f"Disk usage {disk}% exceeded threshold {THRESHOLDS['disk_usage']}%",
        ))
        created += 1

    lat = metrics.get("latency_ms")
    if lat is not None and lat > THRESHOLDS["latency_ms"]:
        db.session.add(Event(
            device_id=device_id,
            event_type="HIGH_LATENCY",
            severity="MEDIUM",
            description=f"Latency {lat}ms exceeded threshold {THRESHOLDS['latency_ms']}ms",
        ))
        created += 1

    return created