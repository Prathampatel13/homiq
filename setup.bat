@echo off
echo ======================================================================
echo [OKF] HomiQ Project Initialization - Setup Phase
echo ======================================================================

echo [1/3] Setting up Backend Environment...
cd backend
if not exist ".venv" (
    echo Creating Virtual Environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Installing Backend Dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Initializing Local Environment Variables...
    copy .env.example .env
)

echo Backend setup complete.
cd ..

echo [2/3] Setting up Frontend Environment...
cd frontend
echo Installing Frontend Dependencies...
call npm install
echo Frontend setup complete.
cd ..

echo [3/3] Setup complete! 
echo ======================================================================
echo You can now run start.bat to launch HomiQ.
pause
