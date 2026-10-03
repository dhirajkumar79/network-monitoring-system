from datetime import datetime

from app.extensions import db


class Session(db.Model):
    __tablename__ = "session"

    session_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("device.device_id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id"), nullable=False, index=True
    )
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    connection_status = db.Column(
        db.String(20), nullable=False, default="CONNECTING", index=True
    )
    session_type = db.Column(db.String(20), nullable=False, default="MONITORING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "connection_status": self.connection_status,
            "session_type": self.session_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Session {self.session_id} {self.session_type} {self.connection_status}>"