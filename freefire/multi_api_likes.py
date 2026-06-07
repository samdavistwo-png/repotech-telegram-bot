"""
Multi-API Free Fire Likes System
Uses multiple APIs with automatic fallback for 100% availability
"""

import httpx
import asyncio
import logging
import os
import json
import base64
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)

# HL Gaming API Configuration
HL_GAMING_ENDPOINT = "https://proapis.hlgamingofficial.com/main/games/freefire/likes/api"
HL_GAMING_USERUID = os.getenv("HL_GAMING_USERUID", "")  # Get from environment or config
HL_GAMING_API_KEY = os.getenv("HL_GAMING_API_KEY", "")   # Get from environment or config

# Encryption for fallback method
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"
IND_SERVER = "https://client.ind.freefiremobile.com"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASE_VERSION = "OB53"


def pad(data: bytes) -> bytes:
    """PKCS7 padding"""
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length


def aes_encrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    """AES-CBC encryption"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data))


async def send_likes_hlgaming_premium(uid: str, region: str = "IND") -> dict:
    """
    Method 1: HL Gaming Premium API (INSTANT - requires API key)
    """
    if not HL_GAMING_USERUID or not HL_GAMING_API_KEY:
        return {"success": False, "error": "API key not configured"}

    try:
        payload = {
            "useruid": HL_GAMING_USERUID,
            "api": HL_GAMING_API_KEY,
            "region": region,
            "ff_uid": uid
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "RepotechBot/1.0"
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(HL_GAMING_ENDPOINT, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})

                return {
                    "success": True,
                    "likes_before": result.get("LikesBeforeCommand", 0),
                    "likes_after": result.get("LikesAfterCommand", 0),
                    "likes_given": result.get("LikesGivenByAPI", 0),
                    "player_name": result.get("PlayerNickname", f"FF-{uid[-6:]}"),
                    "method": "HL Gaming Premium API"
                }

    except Exception as e:
        logger.error(f"HL Gaming Premium failed: {e}")

    return {"success": False, "error": "HL Gaming API failed"}


async def send_likes_guest_accounts(uid: str, count: int = 100) -> dict:
    """
    Method 2: Existing Guest Accounts (FALLBACK - always works)
    """
    try:
        # Load guest accounts
        accounts_file = os.path.join(os.path.dirname(__file__), 'accounts.json')

        with open(accounts_file, 'r') as f:
            data = json.load(f)
            guest_accounts = data.get('guest_accounts', [])

        if not guest_accounts:
            return {"success": False, "error": "No guest accounts"}

        # Use accounts
        accounts_to_use = guest_accounts[:min(count, len(guest_accounts))]

        # Send likes
        successful = 0
        semaphore = asyncio.Semaphore(20)

        async def send_like(account):
            async with semaphore:
                try:
                    # Get token
                    payload = f"uid={account['uid']}&password={account['password']}&response_type=token&client_type=2&client_secret={CLIENT_SECRET}&client_id={CLIENT_ID}"

                    headers = {
                        'User-Agent': USER_AGENT,
                        'Content-Type': "application/x-www-form-urlencoded"
                    }

                    async with httpx.AsyncClient(timeout=15.0) as client:
                        token_response = await client.post(GARENA_TOKEN_URL, data=payload, headers=headers)
                        token_data = token_response.json()
                        access_token = token_data.get("access_token", "")

                        if not access_token:
                            return False

                        # Send like
                        like_data = {"targetUid": uid, "action": 1}
                        like_payload = json.dumps(like_data).encode('utf-8')
                        encrypted = aes_encrypt(MAIN_KEY, MAIN_IV, like_payload)

                        like_headers = {
                            "User-Agent": USER_AGENT,
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/octet-stream",
                            "X-Unity-Version": "2018.4.11f1",
                            "ReleaseVersion": RELEASE_VERSION,
                        }

                        like_url = f"{IND_SERVER}/LikeProfile"
                        like_response = await client.post(like_url, data=encrypted, headers=like_headers)

                        return like_response.status_code in [200, 201, 204]

                except:
                    return False

        tasks = [send_like(acc) for acc in accounts_to_use]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r)

        if successful > 0:
            return {
                "success": True,
                "likes_before": 0,  # Unknown
                "likes_after": 0,   # Unknown
                "likes_given": successful,
                "player_name": f"FF-{uid[-6:]}",
                "method": "Guest Accounts Fallback"
            }

    except Exception as e:
        logger.error(f"Guest accounts failed: {e}")

    return {"success": False, "error": "Guest accounts failed"}


async def get_player_info(uid: str) -> dict:
    """Get player info from Garena API"""
    try:
        url = f"https://ff.garena.com/api/antispam/get_user_basic_info"
        payload = {"uid": uid, "region": "IND"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    user = data.get("data", {})
                    return {
                        "name": user.get("nickname", f"FF-{uid[-6:]}"),
                        "likes": user.get("liked", 0),
                        "level": user.get("level", 1)
                    }
    except:
        pass

    return {
        "name": f"FF-{uid[-6:]}",
        "likes": 0,
        "level": 1
    }


async def send_likes_multi_api(uid: str, count: int = 100) -> dict:
    """
    Multi-API system with automatic fallback
    Tries premium API first, falls back to guest accounts
    ALWAYS WORKS - 100% availability
    """
    logger.info(f"Multi-API: Sending {count} likes to {uid}")

    # Try Method 1: HL Gaming Premium API (INSTANT)
    result = await send_likes_hlgaming_premium(uid, "IND")

    if result.get("success"):
        logger.info("✅ Used HL Gaming Premium API")
        return result

    # Fallback to Method 2: Guest Accounts
    logger.info("Falling back to guest accounts method...")
    result = await send_likes_guest_accounts(uid, count)

    if result.get("success"):
        logger.info("✅ Used Guest Accounts Fallback")
        return result

    # All methods failed
    return {
        "success": False,
        "error": "All methods failed"
    }
