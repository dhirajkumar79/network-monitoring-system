from datetime import datetime

from app.extensions import db


class Device(db.Model):
    __tablename__ = "device"

    device_id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(120), nullable=False)
    hostname = db.Column(db.String(120), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    mac_address = db.Column(db.String(17), nullable=True)
    operating_system = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="UNKNOWN", index=True)
    location = db.Column(db.String(120), nullable=True)
    last_active_time = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "operating_system": self.operating_system,
            "status": self.status,
            "location": self.location,
            "last_active_time": self.last_active_time.isoformat()
            if self.last_active_time
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Device {self.device_name} ({self.status})>"