"""
API Health Check command handler for RepotechBot
Monitors Free Fire API endpoint status
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_only
import logging
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# API endpoints to monitor
ENDPOINTS = {
    "Garena OAuth (Direct Method)": "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant",
    "Free Fire Login (ggblueshark) - LEGACY": "https://loginbp.ggblueshark.com/MajorLogin",
    "Free Fire IND Server": "https://client.ind.freefiremobile.com/LikeProfile",
    "Free Fire US Server": "https://client.us.freefiremobile.com/LikeProfile",
    "Free Fire SG Server": "https://client.sg.freefiremobile.com/LikeProfile",
}


async def check_endpoint(name: str, url: str, timeout: int = 5) -> dict:
    """Check if an endpoint is accessible

    Returns:
        dict: {"name": str, "url": str, "status": str, "code": int or None, "time": float}
    """
    start_time = asyncio.get_event_loop().time()

    try:
        async with httpx.AsyncClient() as client:
            # Use HEAD request for faster checks, fallback to POST for endpoints that require it
            if "MajorLogin" in url or "LikeProfile" in url:
                # These endpoints expect POST with specific data
                response = await client.post(
                    url,
                    data=b"test",  # Dummy data
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=timeout,
                    follow_redirects=False
                )
            elif "oauth/guest/token/grant" in url:
                # OAuth endpoint expects POST with form data
                response = await client.post(
                    url,
                    data="uid=test&password=test&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=timeout,
                    follow_redirects=False
                )
            else:
                response = await client.head(url, timeout=timeout, follow_redirects=False)

            elapsed = asyncio.get_event_loop().time() - start_time

            # Consider 2xx, 3xx, 4xx as "accessible" (server is responding)
            # 503 or timeout means server is down
            if response.status_code == 503:
                return {
                    "name": name,
                    "url": url,
                    "status": "❌ Down (503)",
                    "code": 503,
                    "time": elapsed
                }
            elif 200 <= response.status_code < 500:
                return {
                    "name": name,
                    "url": url,
                    "status": "✅ Online",
                    "code": response.status_code,
                    "time": elapsed
                }
            else:
                return {
                    "name": name,
                    "url": url,
                    "status": f"⚠️ HTTP {response.status_code}",
                    "code": response.status_code,
                    "time": elapsed
                }

    except httpx.TimeoutException:
        elapsed = timeout
        return {
            "name": name,
            "url": url,
            "status": "❌ Timeout",
            "code": None,
            "time": elapsed
        }
    except httpx.ConnectError:
        elapsed = asyncio.get_event_loop().time() - start_time
        return {
            "name": name,
            "url": url,
            "status": "❌ Connection Failed",
            "code": None,
            "time": elapsed
        }
    except Exception as e:
        elapsed = asyncio.get_event_loop().time() - start_time
        return {
            "name": name,
            "url": url,
            "status": f"❌ Error: {str(e)[:20]}",
            "code": None,
            "time": elapsed
        }


@admin_only
async def apihealth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /apihealth command - Check Free Fire API endpoints status"""

    # Send initial message
    status_msg = await update.message.reply_text(
        "🔍 Checking Free Fire API endpoints...\n"
        "⏳ This may take a few seconds..."
    )

    # Check all endpoints concurrently
    tasks = [check_endpoint(name, url) for name, url in ENDPOINTS.items()]
    results = await asyncio.gather(*tasks)

    # Build status message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = "🏥 **Free Fire API Health Check**\n\n"

    # Overall status
    all_online = all(r["status"].startswith("✅") for r in results)
    oauth_down = any("oauth/guest/token/grant" in r["url"] and r["status"].startswith("❌") for r in results)
    ggblueshark_down = any("ggblueshark" in r["url"] and r["status"].startswith("❌") for r in results)
    all_game_servers_down = all(
        r["status"].startswith("❌") for r in results
        if "freefiremobile.com" in r["url"]
    )

    if all_online:
        message += "🟢 **Overall Status: ALL SYSTEMS OPERATIONAL**\n\n"
    elif oauth_down and all_game_servers_down:
        message += "🔴 **Overall Status: CRITICAL - ALL SERVICES DOWN**\n"
        message += "⚠️ Both authentication and game servers are down.\n\n"
    elif oauth_down:
        message += "🔴 **Overall Status: CRITICAL - OAUTH DOWN**\n"
        message += "⚠️ Guest likes will not work. HL Gaming fallback is active.\n\n"
    elif ggblueshark_down and not oauth_down:
        message += "🟡 **Overall Status: LEGACY SERVICE DOWN (OK)**\n"
        message += "✅ ggblueshark is down, but Direct OAuth is working!\n"
        message += "💡 Guest likes using new Direct OAuth method.\n\n"
    else:
        message += "🟡 **Overall Status: PARTIAL OUTAGE**\n\n"

    # Individual endpoint details
    message += "📊 **Endpoint Status:**\n\n"

    for result in results:
        message += f"**{result['name']}**\n"
        message += f"Status: {result['status']}\n"

        if result['code']:
            message += f"HTTP Code: {result['code']}\n"

        message += f"Response Time: {result['time']:.2f}s\n"
        message += f"URL: `{result['url']}`\n\n"

    # Recommendations
    message += "💡 **What This Means:**\n\n"

    if oauth_down and all_game_servers_down:
        message += (
            "🔴 **CRITICAL FAILURE**\n"
            "• Both OAuth and game servers are down\n"
            "• /likes command will not work at all\n"
            "• System will fallback to HL Gaming only\n\n"
            "**Recommended Actions:**\n"
            "1. Wait 10-30 minutes and check again\n"
            "2. All services are external, outside our control\n"
            "3. Users won't be charged if service fails\n"
        )
    elif oauth_down:
        message += (
            "🔴 **OAuth Server is DOWN**\n"
            "• Guest likes method will not work\n"
            "• System will use HL Gaming fallback\n"
            "• This is a Garena service outside our control\n\n"
            "**Recommended Actions:**\n"
            "1. Wait for Garena OAuth to recover\n"
            "2. HL Gaming fallback is active\n"
            "3. Users won't be charged if both methods fail\n"
        )
    elif ggblueshark_down and not oauth_down:
        message += (
            "✅ **SYSTEM WORKING (New Method)**\n"
            "• ggblueshark is down, but that's OK!\n"
            "• Bot now uses Direct OAuth method\n"
            "• Guest likes work WITHOUT ggblueshark\n"
            "• /likes command fully operational\n\n"
            "**What Changed:**\n"
            "• Old: Guest → ggblueshark → JWT → Like\n"
            "• New: Guest → OAuth → JWT → Like (Direct)\n"
            "• No dependency on ggblueshark anymore!\n"
        )
    elif all_online:
        message += (
            "✅ **All systems operational!**\n"
            "• /likes command should work normally\n"
            "• Direct OAuth method active\n"
            "• HL Gaming fallback available\n"
            "• No action needed\n"
        )
    else:
        message += (
            "⚠️ **Some endpoints are experiencing issues**\n"
            "• Check individual statuses above\n"
            "• Bot may have reduced functionality\n"
        )

    message += f"\n⏰ **Checked at:** {current_time}"

    # Update message with results
    await status_msg.edit_text(message, parse_mode="Markdown")

    logger.info(f"API health check completed by admin. Critical down: {critical_down}")
