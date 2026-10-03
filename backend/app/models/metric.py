from datetime import datetime

from app.extensions import db


class NetworkMetric(db.Model):
    __tablename__ = "network_metric"

    metric_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("device.device_id"), nullable=False, index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    latency_ms = db.Column(db.Float, nullable=True)
    cpu_usage = db.Column(db.Float, nullable=True)
    memory_usage = db.Column(db.Float, nullable=True)
    disk_usage = db.Column(db.Float, nullable=True)
    network_upload = db.Column(db.Float, nullable=True)
    network_download = db.Column(db.Float, nullable=True)
    packet_loss = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "metric_id": self.metric_id,
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "latency_ms": self.latency_ms,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_upload": self.network_upload,
            "network_download": self.network_download,
            "packet_loss": self.packet_loss,
        }

    def __repr__(self):
        return f"<Metric device={self.device_id} cpu={self.cpu_usage}>"