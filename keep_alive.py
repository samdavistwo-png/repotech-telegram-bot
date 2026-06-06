"""
Keep Alive module for RepotechBot
Runs a simple Flask web server for 24/7 uptime monitoring
"""

from flask import Flask
from threading import Thread
from config import KEEP_ALIVE_PORT
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def home():
    """Health check endpoint"""
    return "Bot is alive!"


@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "RepotechBot is running"}


def run():
    """Run Flask server"""
    logger.info(f"Starting Keep Alive server on port {KEEP_ALIVE_PORT}")
    app.run(host='0.0.0.0', port=KEEP_ALIVE_PORT, debug=False, use_reloader=False)


def keep_alive():
    """Start Flask server in a separate thread"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    logger.info("Keep Alive server started")
