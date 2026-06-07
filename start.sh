#!/bin/bash

# Start script for running both auth server and Telegram bot
# This allows both services to run in a single Railway service

# Start auth server in background on port 8001
uvicorn auth_server:app --host 0.0.0.0 --port 8001 &
AUTH_PID=$!

echo "Auth server started on port 8001 (PID: $AUTH_PID)"

# Wait a moment for auth server to start
sleep 2

# Start Telegram bot (this runs in foreground)
python bot.py &
BOT_PID=$!

echo "Telegram bot started (PID: $BOT_PID)"

# Wait for both processes
wait $AUTH_PID $BOT_PID
