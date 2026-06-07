"""
Optimized Free Fire Likes Engine
Based on: https://github.com/kaifcodec/freefire-like-and-guest-api
Super fast concurrent processing with RPS limiting
"""

import httpx
import asyncio
import json
import base64
import os
from Crypto.Cipher import AES
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Encryption Configuration
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

# API Configuration
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"
IND_SERVER = "https://client.ind.freefiremobile.com"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASE_VERSION = "OB53"

# Performance Configuration
MAX_CONCURRENT = 50  # Increased from 20 for speed
REQUEST_TIMEOUT = 10.0  # Reduced for faster failure detection


def pad(data: bytes) -> bytes:
    """PKCS7 padding"""
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length


def aes_encrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    """AES-CBC encryption"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data))


async def get_jwt_token(uid: str, password: str) -> str:
    """Get JWT token for guest account - OPTIMIZED"""
    try:
        payload = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret={CLIENT_SECRET}&client_id={CLIENT_ID}"

        headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': "application/x-www-form-urlencoded",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip"
        }

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(GARENA_TOKEN_URL, data=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return data.get("access_token", "")
    except:
        pass

    return ""


async def send_like_optimized(guest_uid: str, guest_password: str, target_uid: str, semaphore: asyncio.Semaphore) -> bool:
    """
    Send like with optimized concurrent processing
    Based on kaifcodec's architecture
    """
    async with semaphore:
        try:
            # Get JWT
            jwt_token = await get_jwt_token(guest_uid, guest_password)

            if not jwt_token:
                logger.debug(f"Failed to get JWT for guest {guest_uid}")
                return False

            # Build encrypted protobuf payload
            like_payload = {
                "targetUid": target_uid,
                "action": 1  # 1 = like
            }

            payload_bytes = json.dumps(like_payload).encode('utf-8')
            encrypted_payload = aes_encrypt(MAIN_KEY, MAIN_IV, payload_bytes)

            # Send to LikeProfile endpoint
            headers = {
                "User-Agent": USER_AGENT,
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/octet-stream",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": RELEASE_VERSION,
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }

            like_url = f"{IND_SERVER}/LikeProfile"

            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(like_url, data=encrypted_payload, headers=headers)
                return response.status_code in [200, 201, 204]

        except:
            return False


async def send_likes_super_fast(target_uid: str, count: int = 100) -> Dict:
    """
    SUPER FAST likes delivery with optimized concurrent processing
    Uses kaifcodec's proven architecture with 50 concurrent requests
    """
    try:
        # Load guest accounts
        accounts_file = os.path.join(os.path.dirname(__file__), 'accounts.json')

        with open(accounts_file, 'r') as f:
            data = json.load(f)
            guest_accounts = data.get('guest_accounts', [])

        if not guest_accounts:
            return {
                "success": False,
                "sent": 0,
                "failed": count,
                "error": "No guest accounts available"
            }

        # Select accounts
        accounts_to_use = guest_accounts[:min(count, len(guest_accounts))]

        # Concurrent processing with RPS limiting
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)

        # Send all likes concurrently
        tasks = [
            send_like_optimized(acc['uid'], acc['password'], target_uid, semaphore)
            for acc in accounts_to_use
        ]

        # Execute all tasks
        results = await asyncio.gather(*tasks)

        # Count results
        successful = sum(1 for r in results if r)
        failed = len(results) - successful

        return {
            "success": successful > 0,
            "sent": successful,
            "failed": failed,
            "total": len(results),
            "method": "Optimized Engine (50 concurrent)"
        }

    except Exception as e:
        logger.error(f"Optimized engine error: {e}", exc_info=True)
        return {
            "success": False,
            "sent": 0,
            "failed": count,
            "error": f"{type(e).__name__}: {str(e)}"
        }


async def get_player_info_fast(uid: str) -> Dict:
    """Get player info from Garena API - FAST"""
    try:
        url = f"https://ff.garena.com/api/antispam/get_user_basic_info"
        payload = {"uid": uid, "region": "IND"}

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(url, json=payload, headers=headers)

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
