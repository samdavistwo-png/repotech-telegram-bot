"""
Run both auth server and Telegram bot simultaneously
"""

import subprocess
import sys
import time
import os

def main():
    print("=" * 70)
    print("🚀 STARTING REPOTECH BOT WITH AUTHENTICATION SERVER")
    print("=" * 70)
    print("📡 Auth server will run on port 8001")
    print("🤖 Bot will connect to localhost:8001 for authentication")
    print("=" * 70)

    # Start auth server in background (with output visible)
    print("\n[1/2] Starting auth server on port 8001...")
    auth_server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "auth_server:app", "--host", "0.0.0.0", "--port", "8001"],
        # Don't capture output - let it print directly to console
    )
    print(f"✅ Auth server started (PID: {auth_server.pid})")

    # Wait for auth server to initialize
    print("⏳ Waiting 3 seconds for auth server to initialize...")
    time.sleep(3)

    # Start Telegram bot in foreground (with output visible)
    print("\n[2/2] Starting Telegram bot...")
    bot = subprocess.Popen(
        [sys.executable, "bot.py"],
        # Don't capture output - let it print directly to console
    )
    print(f"✅ Telegram bot started (PID: {bot.pid})")

    print("\n" + "=" * 70)
    print("✅ BOTH SERVICES ARE NOW RUNNING")
    print("=" * 70)
    print("📡 Auth server: http://localhost:8001")
    print("📡 Auth server health: http://localhost:8001/health")
    print("🤖 Telegram bot: Active and polling for messages")
    print("=" * 70 + "\n")

    # Monitor both processes
    try:
        while True:
            # Check if auth server crashed
            if auth_server.poll() is not None:
                print(f"\n❌ ERROR: Auth server exited with code {auth_server.returncode}")
                print("Terminating bot...")
                bot.terminate()
                sys.exit(1)

            # Check if bot crashed
            if bot.poll() is not None:
                print(f"\n❌ ERROR: Bot exited with code {bot.returncode}")
                print("Terminating auth server...")
                auth_server.terminate()
                sys.exit(1)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("🛑 SHUTTING DOWN SERVICES")
        print("=" * 70)
        print("Terminating auth server...")
        auth_server.terminate()
        print("Terminating bot...")
        bot.terminate()
        print("✅ Shutdown complete")
        sys.exit(0)

if __name__ == "__main__":
    main()
