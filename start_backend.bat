@echo off
echo ===================================================
echo [NEXUS AI] Launching Autonomous Operations Backend...
echo ===================================================
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
