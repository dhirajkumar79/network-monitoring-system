from datetime import datetime

from app.extensions import db


class MonitoringTool(db.Model):
    __tablename__ = "monitoring_tool"

    tool_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("device.device_id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "tool_id": self.tool_id,
            "device_id": self.device_id,
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<MonitoringTool {self.name} {self.version}>"