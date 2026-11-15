@echo off
echo ===================================================================
echo [NEXUS AI] Autonomous IT Operations & Incident Resolution Platform
echo ===================================================================
echo Starting Backend API Server (Port 8000)...
start "NEXUS AI - Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting React Enterprise Frontend (Port 3000)...
start "NEXUS AI - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo NEXUS AI is initializing:
echo - Frontend Dashboard: http://localhost:3000
echo - Backend API Docs:   http://localhost:8000/docs
echo - WebSocket Stream:   ws://localhost:8000/ws/events
echo ===================================================================
