#!/bin/bash

echo "=== ProManage Backend Setup ==="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To create a superuser, run:"
echo "  python manage.py createsuperuser"
echo ""
echo "To start the server, run:"
echo "  python manage.py runserver"
echo ""
