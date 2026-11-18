@echo off
echo ============================================
echo  FoodFlow - Backend (Spring Boot + H2 Dev)
echo ============================================
set JAVA_HOME=C:\Program Files\Java\jdk-21
cd /d "C:\Users\opsir\Desktop\collage project\backend"
echo Starting Spring Boot on http://localhost:8080
echo Using H2 in-memory database (dev profile)
echo.
"C:\Program Files\Java\jdk-21\bin\java.exe" -jar target\foodflow-backend-1.0.0.jar --spring.profiles.active=dev
pause
