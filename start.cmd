@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo venv not found at "%~dp0venv". Create it first with: python -m venv venv
    pause
    exit /b 1
)

echo Starting OfficeMind backend (FastAPI) on port 8000...
start "OfficeMind Backend" cmd /k ""%~dp0venv\Scripts\activate.bat" && python -m uvicorn backend.main:app --port 8000 --reload"

echo Waiting for the backend to finish starting (this can take 15-30s the
echo first time, while it loads the Whisper speech model)...
set WAITED=0
:waitloop
curl -s -o nul -m 2 http://127.0.0.1:8000/health
if %errorlevel%==0 goto backend_ready
set /a WAITED+=2
if %WAITED% geq 90 (
    echo.
    echo Backend is still not responding after 90s. Check the "OfficeMind Backend"
    echo window for errors. Continuing anyway...
    goto backend_done_waiting
)
timeout /t 2 /nobreak >nul
goto waitloop

:backend_ready
echo Backend is up.
:backend_done_waiting

echo Starting OfficeMind frontend (Flask) on port 5000...
start "OfficeMind Frontend" cmd /k ""%~dp0venv\Scripts\activate.bat" && python frontend\app.py"

echo Waiting for the frontend to finish starting...
set WAITED=0
:waitloop2
curl -s -o nul -m 2 http://127.0.0.1:5000/health
if %errorlevel%==0 goto frontend_ready
set /a WAITED+=1
if %WAITED% geq 30 goto frontend_done_waiting
timeout /t 1 /nobreak >nul
goto waitloop2

:frontend_ready
echo Frontend is up.
:frontend_done_waiting

echo.
echo Backend:  http://127.0.0.1:8000/health
echo Frontend: http://127.0.0.1:5000
echo.
start "" "http://127.0.0.1:5000"

endlocal
