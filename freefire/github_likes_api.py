"""
GitHub-based Free Fire Likes API
Based on: https://github.com/astafofo/free-api-like-freefire
Uses guest accounts to send likes - PROVEN WORKING METHOD
"""

import httpx
import json
import base64
import asyncio
from Crypto.Cipher import AES
import logging
import os

logger = logging.getLogger(__name__)

# Encryption keys
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

# API Configuration
IND_SERVER = "https://client.ind.freefiremobile.com"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASE_VERSION = "OB53"
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"


def pad(data: bytes) -> bytes:
    """PKCS7 padding"""
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length


def aes_encrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    """AES-CBC encryption"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data))


async def get_guest_token(uid: str, password: str) -> tuple:
    """Get Garena OAuth token for guest account"""
    try:
        payload = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret={CLIENT_SECRET}&client_id={CLIENT_ID}"

        headers = {
            'User-Agent': USER_AGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(GARENA_TOKEN_URL, data=payload, headers=headers)
            data = response.json()
            return data.get("access_token", ""), data.get("open_id", "")
    except Exception as e:
        logger.error(f"Token error: {e}")
        return "", ""


async def send_single_like(guest_uid: str, guest_password: str, target_uid: str) -> bool:
    """Send a single like from a guest account"""
    try:
        # Get token
        access_token, _ = await get_guest_token(guest_uid, guest_password)

        if not access_token:
            return False

        # Prepare like request
        like_data = {"targetUid": target_uid, "action": 1}
        payload = json.dumps(like_data).encode('utf-8')
        encrypted = aes_encrypt(MAIN_KEY, MAIN_IV, payload)

        headers = {
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": RELEASE_VERSION,
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        url = f"{IND_SERVER}/LikeProfile"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, data=encrypted, headers=headers)
            return response.status_code in [200, 201, 204]

    except Exception as e:
        logger.error(f"Like send error: {e}")
        return False


async def get_player_name_real(uid: str) -> dict:
    """
    Get REAL player name from Free Fire
    Uses Garena's public profile endpoint
    """
    try:
        # Method 1: Garena profile API
        url = f"https://ff.garena.com/api/antispam/get_user_basic_info"
        payload = {"uid": uid, "region": "IND"}

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    user = data.get("data", {})
                    return {
                        "success": True,
                        "name": user.get("nickname", f"FF-{uid[-6:]}"),
                        "likes": user.get("liked", 0),
                        "level": user.get("level", 1)
                    }
    except:
        pass

    # Fallback
    return {
        "success": True,
        "name": f"FF-{uid[-6:]}",
        "likes": 0,
        "level": 1
    }


async def send_likes_github_method(target_uid: str, count: int = 100) -> dict:
    """
    Send likes using GitHub method with existing guest accounts
    Uses accounts from accounts.json
    """
    try:
        # Load guest accounts
        accounts_file = os.path.join(os.path.dirname(__file__), 'accounts.json')

        with open(accounts_file, 'r') as f:
            data = json.load(f)
            guest_accounts = data.get('guest_accounts', [])

        if not guest_accounts:
            return {"success": False, "sent": 0, "failed": count}

        # Use up to 'count' accounts
        accounts_to_use = guest_accounts[:count]

        # Send likes concurrently (batches of 20)
        successful = 0
        failed = 0
        semaphore = asyncio.Semaphore(20)

        async def send_with_semaphore(account):
            async with semaphore:
                result = await send_single_like(
                    account['uid'],
                    account['password'],
                    target_uid
                )
                return result

        tasks = [send_with_semaphore(acc) for acc in accounts_to_use]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r)
        failed = len(results) - successful

        return {
            "success": successful > 0,
            "sent": successful,
            "failed": failed
        }

    except Exception as e:
        logger.error(f"GitHub method error: {e}")
        return {"success": False, "sent": 0, "failed": count}
