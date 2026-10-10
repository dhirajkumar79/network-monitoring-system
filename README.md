# Network Monitoring and Remote Desktop System

A centralized system for monitoring multiple client computers over a network
and requesting authorized remote desktop sessions - built with a Flask backend,
a React admin dashboard, and a Python client agent.

## Overview

This project provides administrators with a web dashboard to:

- Monitor devices on the network (CPU, RAM, disk, network, latency)
- See device online/offline status in real time
- Receive alerts when metrics exceed thresholds
- View event and session history
- Request authorized remote desktop sessions using Microsoft Remote Desktop
- Generate and export reports (CSV)

**Security note:** This system uses only legitimate, authorized remote-access
mechanisms (Microsoft Remote Desktop / RDP). It does not implement covert
remote control, credential theft, or any form of malware functionality.

## Architecture

    ADMIN (Browser)
          |
          v
    React Admin Dashboard
          |
    HTTP / WebSocket (Socket.IO)
          |
          v
    Flask Backend API
          |
    +-----+-----+-----+
    |     |     |     |
    v     v     v     v
   MySQL  Monitoring  Remote Session
 Database  Service    Manager
          |
          v
    Client Agent API
          |
    +-----+-----+-----+
    |     |     |     |
    v     v     v     v
  Client 1  Client 2  Client 3

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-SocketIO |
| Database | MySQL 8 |
| Frontend | React 19, Vite 8, Tailwind CSS 4, Recharts, Axios, React Router |
| Client Agent | Python 3.12, psutil, requests |
| Testing | Pytest (24 tests) |

## Project Structure

    network-monitoring-system/
    +-- backend/          Flask API + WebSocket + tests
    +-- client_agent/     Python agent that runs on monitored PCs
    +-- frontend/         React admin dashboard
    +-- docs/             Setup, demo, and API docs

## Quick Start

See docs/SETUP.md for full setup instructions.

TL;DR - Open 3 terminals:

Terminal 1 - Backend:

    cd backend
    .\.venv\Scripts\Activate.ps1
    python run.py

Terminal 2 - Client Agent:

    cd client_agent
    .\.venv\Scripts\Activate.ps1
    python -m agent.main

Terminal 3 - Frontend:

    cd frontend
    npm run dev

Open http://localhost:5173 and log in with your admin credentials.

## Running Tests

    cd backend
    .\.venv\Scripts\Activate.ps1
    pytest

Expected: 24 passed.

## Documentation

- docs/SETUP.md - Setup Guide
- docs/API.md - API Reference
- docs/DEMO.md - Demo Script

## Security Features

- JWT authentication with 8-hour token expiry
- Passwords hashed with Werkzeug (never stored plaintext)
- Role-based access control (ADMIN / VIEWER) enforced server-side
- Device tokens generated with secrets.token_urlsafe(48) and stored hashed
- All remote sessions are logged with user_id, device_id, and timestamps
- Remote access uses legitimate Windows Remote Desktop - no covert channels

## Author

[Dhiraj kumar] - [IGNOU]