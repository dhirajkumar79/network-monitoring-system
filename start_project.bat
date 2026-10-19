@echo off
title Network Monitoring System - Launcher
echo Starting all services...
start "NMS Backend" cmd /k "cd backend && .venv\Scripts\activate && python run.py"
start "NMS Frontend" cmd /k "cd frontend && npm run dev"
start "NMS Agent" cmd /k "cd client_agent && .venv\Scripts\activate && python -m agent.main"
echo All services started! You can close this small window.
timeout /t 3 >nul
