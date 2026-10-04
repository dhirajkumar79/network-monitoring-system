"""Socket.IO event handlers and broadcast helpers."""
from flask import request
from flask_socketio import emit, join_room
from app.extensions import socketio
def register_socketio_handlers():
    """Register handlers on the shared socketio object."""
    @socketio.on("connect")
    def on_connect():
        print(f"[socketio] Client connected: {request.sid}")
        emit("server_message", {"message": "Connected to Network Monitoring System"})
    @socketio.on("disconnect")
    def on_disconnect():
        print(f"[socketio] Client disconnected: {request.sid}")
    @socketio.on("subscribe_dashboard")
    def on_subscribe():
        join_room("dashboard")
        print(f"[socketio] Client {request.sid} joined dashboard room")
def broadcast_event(event_name: str, payload: dict):
    """Send a message to all clients in the 'dashboard' room.
    Safe to call from any request context or background thread.
    """
    try:
        socketio.emit(event_name, payload, room="dashboard")
    except Exception as exc:
        print(f"[socketio] Broadcast error: {exc}")
