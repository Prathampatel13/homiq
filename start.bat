@echo off
echo ======================================================================
echo [OKG] HomiQ Project Launch Sequence
echo ======================================================================

echo Starting Backend Server (Port 8000)...
start "HomiQ Backend" cmd /k "cd backend && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

echo Starting Frontend Server (Port 3000)...
start "HomiQ Frontend" cmd /k "cd frontend && npm run dev"

echo ======================================================================
echo Servers are launching in separate windows!
echo Backend API Docs: http://127.0.0.1:8000/docs
echo Frontend App: http://localhost:3000
echo ======================================================================
