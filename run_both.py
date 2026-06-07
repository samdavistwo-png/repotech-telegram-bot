"""
Run both auth server and Telegram bot simultaneously
"""

import subprocess
import sys
import time
import os

def main():
    print("Starting both Auth Server and Telegram Bot...")

    # Start auth server in background
    print("Starting auth server on port 8001...")
    auth_server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "auth_server:app", "--host", "0.0.0.0", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    print(f"Auth server started (PID: {auth_server.pid})")

    # Wait a moment for auth server to start
    time.sleep(2)

    # Start Telegram bot in foreground
    print("Starting Telegram bot...")
    bot = subprocess.Popen(
        [sys.executable, "bot.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    print(f"Telegram bot started (PID: {bot.pid})")

    # Stream output from both processes
    try:
        while True:
            # Check if processes are still running
            if auth_server.poll() is not None:
                print(f"Auth server exited with code {auth_server.returncode}")
                bot.terminate()
                sys.exit(1)

            if bot.poll() is not None:
                print(f"Bot exited with code {bot.returncode}")
                auth_server.terminate()
                sys.exit(1)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        auth_server.terminate()
        bot.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
