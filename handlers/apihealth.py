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
    "Garena OAuth": "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant",
    "Free Fire Login (ggblueshark)": "https://loginbp.ggblueshark.com/MajorLogin",
    "Free Fire IND Server": "https://client.ind.freefiremobile.com/LikeProfile",
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
    critical_down = any("ggblueshark" in r["url"] and r["status"].startswith("❌") for r in results)

    if all_online:
        message += "🟢 **Overall Status: ALL SYSTEMS OPERATIONAL**\n\n"
    elif critical_down:
        message += "🔴 **Overall Status: CRITICAL SERVICE DOWN**\n"
        message += "⚠️ Likes command will not work until ggblueshark is back online.\n\n"
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

    if critical_down:
        message += (
            "🔴 **ggblueshark Login Server is DOWN**\n"
            "• /likes command will fail\n"
            "• This is a third-party service outside our control\n"
            "• Users won't be charged coins when it fails\n\n"
            "**Recommended Actions:**\n"
            "1. Wait 10-30 minutes and check again\n"
            "2. Monitor this endpoint periodically\n"
            "3. Consider implementing your own auth server\n"
            "4. Notify users of temporary service disruption\n"
        )
    elif all_online:
        message += (
            "✅ **All systems operational!**\n"
            "• /likes command should work normally\n"
            "• All authentication flows are functional\n"
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
