# Setup Guide

Complete instructions to run this project from scratch on Windows.

## Prerequisites

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.12+ | https://www.python.org/downloads/ |
| Node.js | 20 LTS+ | https://nodejs.org/ |
| MySQL Server | 8.0+ | https://dev.mysql.com/downloads/installer/ |
| Git | Latest | https://git-scm.com/ |

During Python install, check **"Add Python to PATH"**.

## Step 1 - Clone or copy the project

Place the project folder somewhere convenient, e.g. `C:\Users\<you>\network-monitoring-system`.

## Step 2 - Create the MySQL database

Open PowerShell and run:

    mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS network_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

Enter your MySQL root password when prompted.

## Step 3 - Backend setup

    cd backend
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

Edit `backend\.env`:

    FLASK_ENV=development
    SECRET_KEY=<any-long-random-string>
    JWT_SECRET_KEY=<any-long-random-string>
    DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/network_monitoring
    CORS_ORIGINS=http://localhost:5173
    HEARTBEAT_TIMEOUT_SECONDS=60

Run migrations and create the first admin:

    flask db upgrade
    python -m scripts.create_admin

## Step 4 - Frontend setup

In a new PowerShell window:

    cd frontend
    npm install

## Step 5 - Client Agent setup

In another new PowerShell window:

    cd client_agent
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

Edit `client_agent\.env`:

    SERVER_URL=http://127.0.0.1:5000
    HEARTBEAT_INTERVAL=30
    HTTP_TIMEOUT=10
    LOCATION=Lab 1
    DEVICE_NAME=
    REMOTE_DESKTOP_TARGET=

## Step 6 - Start everything

You need 3 terminals running at the same time.

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

## Step 7 - Open the dashboard

Go to http://localhost:5173 and log in with the admin credentials you set.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| python is not recognized | Use py instead, or reinstall Python with "Add to PATH" |
| running scripts is disabled | Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned |
| Access denied for user root | Wrong MySQL password in .env |
| CORS error in browser | Check backend\.env has CORS_ORIGINS=http://localhost:5173 |
| Port 5173 already in use | Kill Node processes: Get-Process node | Stop-Process -Force |
| Frontend Disconnected socket | Backend must be running on port 5000 |
