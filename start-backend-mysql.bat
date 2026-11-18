@echo off
echo ============================================
echo  FoodFlow - Backend (Spring Boot + MySQL)
echo ============================================
set JAVA_HOME=C:\Program Files\Java\jdk-21
cd /d "C:\Users\opsir\Desktop\collage project\backend"
echo Starting Spring Boot on http://localhost:8080
echo Using MySQL database
echo.
echo IMPORTANT: Ensure MySQL is running and credentials in
echo backend\src\main\resources\application.properties are correct.
echo.
"C:\Program Files\Java\jdk-21\bin\java.exe" -jar target\foodflow-backend-1.0.0.jar
pause
