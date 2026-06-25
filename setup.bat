@echo off

echo === ProManage Backend Setup ===
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo === Setup Complete! ===
echo.
echo To create a superuser, run:
echo   python manage.py createsuperuser
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
pause
