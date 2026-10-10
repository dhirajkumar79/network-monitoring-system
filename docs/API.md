# API Reference

Base URL: `http://127.0.0.1:5000`

Success response: `{ "success": true, "data": { ... } }`
Error response:   `{ "success": false, "message": "..." }`

## Authentication

POST /api/auth/login
Body: username, password
Returns: access_token and user info.

GET /api/auth/me
Headers: Authorization Bearer token
Returns: current user.

POST /api/auth/logout
Headers: Authorization Bearer token
Returns: 200 OK.

## Devices

GET /api/devices
Query: ?status=ONLINE|OFFLINE|UNKNOWN
Returns: list of devices.

GET /api/devices/:id
Returns: single device.

GET /api/devices/:id/metrics
Query: ?limit=50
Returns: recent metrics (newest first).

GET /api/devices/:id/events
Query: ?limit=50
Returns: recent events.

## Events

GET /api/events
Query: ?severity=HIGH&event_type=DEVICE_OFFLINE&device_id=3&since=2025-01-01T00:00:00&limit=100
Returns: filtered events.

## Sessions (Remote Desktop)

GET /api/sessions
Returns: all sessions.

POST /api/sessions
Role: ADMIN only
Body: device_id, session_type
Returns: 201 with session record (connection_status CONNECTING).
Errors: 400 (device offline or already pending), 403 (not admin).

POST /api/sessions/:id/end
Role: ADMIN only
Returns: session with connection_status DISCONNECTED and end_time.

## Reports

GET /api/reports/summary
Query: ?from=YYYY-MM-DD&to=YYYY-MM-DD
Returns: aggregate counts and averages.

GET /api/reports/device-availability
Returns: per-device metric count and average CPU.

GET /api/reports/session-durations
Returns: sessions with duration_seconds.

GET /api/reports/metrics
Query: ?device_id=4&limit=1000
Returns: raw metrics.

## Client Agent (device-authenticated)

All these require header: X-Device-Token: <token>

POST /api/client/register
Body: device_name, hostname, operating_system, ip_address, mac_address, location
Returns: device_id and device_token.

POST /api/client/heartbeat
Body: cpu_usage, memory_usage, disk_usage, latency_ms, network_upload, network_download, packet_loss
Returns: device_id, status, server_time.

GET /api/client/pending-session
Returns: pending CONNECTING session for this device, or null.

POST /api/client/session-status
Body: session_id, status (CONNECTED | DISCONNECTED | FAILED)
Returns: 200 with confirmation.

## WebSocket (Socket.IO)

Events emitted by the server to the dashboard room:

- device_registered
- device_heartbeat
- device_status_change
- new_alert
- session_update

Clients emit subscribe_dashboard to join the room.