# Demo Script

Step-by-step walkthrough for the college demo / viva.

## Setup Before the Demo

Open 3 PowerShell windows:

1. Backend: cd backend, activate venv, python run.py
2. Agent: cd client_agent, activate venv, python -m agent.main
3. Frontend: cd frontend, npm run dev

Open browser at http://localhost:5173.

## Demo Steps

### 1. Show the login page
- Open http://localhost:5173
- It redirects to /login
- Point out: no dashboard access without login

### 2. Log in as admin
- Username: Admin1234, Password: 230049
- Click Login
- Land on Dashboard

### 3. Dashboard
- Show Total / Online / Offline stat cards
- Point out the green pulsing dot: "Live updates active" - proves Socket.IO
- Show the Devices table with last-active time
- Show the Recent Events list including real HIGH_MEMORY alerts

### 4. Devices page
- Click Devices in the nav
- Show the table with OS, IP, Status, Last Active
- Click ONLINE filter button
- Click View on the online device

### 5. Device Detail
- Show 4 info cards: IP, MAC, OS, Location
- Show CPU and Memory chart with real data points
- Show Latency chart with real latency spikes
- Explain: agent collects these every 30 seconds using psutil

### 6. Alerts page
- Click Alerts in the nav
- Show events with severity badges
- Click HIGH filter
- Explain: when metrics exceed a threshold, server automatically creates an event

### 7. Real-time test (the wow moment)
- In the agent window, press Ctrl + C to stop it
- Do NOT refresh the browser
- Wait about 90 seconds
- Watch the device flip to OFFLINE by itself
- Say: "No refresh needed - that's Socket.IO pushing updates"
- Restart the agent: python -m agent.main
- Within 30 seconds it flips back to ONLINE

### 8. Remote Session workflow
- Go to Devices, click View on the ONLINE device
- Click Start Remote Session, confirm
- Popup: Session N created (CONNECTING)
- On the agent window, point out:
  [remote] session N requested
  [remote] session N -> CONNECTED
  [remote] launched mstsc (target=none)
- A Windows Remote Desktop window pops up - this is the legitimate Microsoft client
- Say: agent only launches the OS official remote desktop tool, no covert protocol
- Go to Sessions page - session shows CONNECTED (green)
- Click End - session flips to DISCONNECTED with a timestamp

### 9. Reports
- Click Reports in the nav
- Change the Range dropdown (24h / 7d / 30d) - numbers update
- Point out: Total Devices, Sessions, High Alerts, Avg CPU, Avg Memory, Avg Latency
- Click Download CSV on Device Availability - a file downloads
- Open it in Excel to show real data

### 10. Authorization test
- Explain: VIEWER role cannot start sessions
- The backend returns 403 - the button isn't the security, the backend is

### 11. Show the test suite
- In the backend window: pytest
- Show: 24 passed
- Say: tests cover auth, registration, heartbeats, alerts, sessions, authorization

### 12. Show the code structure
- Open VS Code with the project
- Point out clean folder structure:
  - backend/app/models/ - 6 SQLAlchemy models
  - backend/app/routes/ - blueprints for each domain
  - backend/app/services/ - business logic
  - backend/app/tasks/ - background offline checker
  - backend/app/websocket/ - Socket.IO events
  - client_agent/agent/ - modular agent
  - frontend/src/pages/ - React pages

## Talking Points

Architecture:
"The system has three tiers - Flask backend, React frontend, and Python client agents. They communicate via REST for CRUD and Socket.IO for real-time events."

Security:
"Passwords are hashed with Werkzeug. Sessions use JWT with 8-hour expiry. Device authentication uses SHA-256 hashed tokens. Remote sessions are authorized server-side with role checks."

Remote Desktop:
"We intentionally use Microsoft's built-in Remote Desktop (mstsc) - a legitimate, standards-compliant tool. The agent only coordinates the workflow; it does not implement any covert remote-control protocol."

Database design:
"Six tables: User, Device, Session, Event, NetworkMetric, MonitoringTool. Migrations are managed by Flask-Migrate / Alembic."

## If Something Fails During the Demo

| Problem | Quick fix |
|---------|-----------|
| Dashboard shows Disconnected | Backend isn't running - start python run.py |
| Devices empty | Agent isn't running - start python -m agent.main |
| Charts are empty | Wait 60s for heartbeats |
| Remote session 400 device not online | Wait 30s, retry |
| Page blank | Hard refresh: Ctrl + Shift + R |
