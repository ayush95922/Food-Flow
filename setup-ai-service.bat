@echo off
echo ============================================
echo  FoodFlow - AI Service Setup
echo ============================================
set PYTHONHOME=C:\Users\opsir\AppData\Local\Python\pythoncore-3.14-64
cd /d "C:\Users\opsir\Desktop\collage project\ai_service"
echo.
echo Step 1: Creating Python virtual environment...
"C:\Users\opsir\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)
echo Done.
echo.
echo Step 2: Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
echo.
echo Step 3: Installing AI service dependencies...
echo (This may take a few minutes - downloading packages)
.venv\Scripts\python.exe -m pip install fastapi uvicorn[standard] pydantic pydantic-settings python-multipart numpy pandas scipy scikit-learn joblib networkx statsmodels httpx Pillow
echo.
echo Step 4: Copying .env file...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Copied .env.example to .env
        echo You may edit .env to add your GROQ_API_KEY if available.
    ) else (
        echo Creating default .env...
        echo FOOD_BACKEND=auto > .env
        echo AI_SERVICE_HOST=0.0.0.0 >> .env
        echo AI_SERVICE_PORT=8000 >> .env
        echo GROQ_API_KEY= >> .env
    )
) else (
    echo .env already exists, skipping.
)
echo.
echo ============================================
echo  Setup Complete!
echo  Run start-ai-service.bat to start the service.
echo ============================================
pause
