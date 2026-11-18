@echo off
echo ============================================
echo  FoodFlow - AI Service (FastAPI + Python)
echo ============================================
set PYTHONHOME=C:\Users\opsir\AppData\Local\Python\pythoncore-3.14-64
cd /d "C:\Users\opsir\Desktop\collage project\ai_service"
echo Starting FastAPI AI Service on http://localhost:8000
echo Docs available at http://localhost:8000/docs
echo.
if not exist ".venv\Scripts\uvicorn.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: setup-ai-service.bat first
    pause
    exit /b 1
)
.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
pause
