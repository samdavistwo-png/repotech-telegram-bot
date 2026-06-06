#!/bin/bash

# RepotechBot - Run Script
# This script helps you set up and run the bot

echo "================================"
echo "RepotechBot - Setup & Run Script"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if .env exists and has ADMIN_ID set
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env from .env.example"
    exit 1
fi

# Check if ADMIN_ID is set
if grep -q "ADMIN_ID=0" .env; then
    echo "WARNING: ADMIN_ID is not set in .env file!"
    echo "Please edit .env and set your Telegram User ID"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully!"
else
    echo "Error installing dependencies!"
    exit 1
fi

echo ""
echo "================================"
echo "Starting RepotechBot..."
echo "================================"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python bot.py
