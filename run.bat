@echo off
cd /d "%~dp0"

echo Stopping any existing Streamlit process on port 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Starting Community App...
echo Access: http://localhost:8501
echo Press Ctrl+C to stop.
echo.

streamlit run main.py --server.port 8501 --server.headless false

pause
