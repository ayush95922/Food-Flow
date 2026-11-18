@echo off
echo =====================================================================
echo    FoodFlow: AI-Assisted Surplus Food Redistribution System
echo =====================================================================
echo.
echo Starting FoodFlow Backend (Port 8080)...
start "FoodFlow Backend" cmd /c "call "%~dp0start-backend.bat""

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting FoodFlow Frontend (Port 5173)...
start "FoodFlow Frontend" cmd /c "call "%~dp0start-frontend.bat""

echo.
echo =====================================================================
echo  Services started in separate windows!
echo.
echo  Frontend URL: http://localhost:5173
echo  Backend API:  http://localhost:8080/api
echo  H2 Console:   http://localhost:8080/h2-console
echo.
echo  Demo Credentials:
echo   - Admin:      admin@foodflow.org         / admin123
echo   - Donor:      donor@greenhotel.com       / donor123
echo   - Receiver:   receiver@hopeorphanage.org   / receiver123
echo   - Volunteer:  volunteer@foodflow.org     / volunteer123
echo =====================================================================
echo.
