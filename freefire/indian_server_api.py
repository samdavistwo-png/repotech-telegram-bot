"""
Free Fire Indian Server API
Fetches REAL player data from IND server
"""

import httpx
import json
import base64
from Crypto.Cipher import AES
import logging

logger = logging.getLogger(__name__)

# Constants
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
IND_SERVER = "https://client.ind.freefiremobile.com"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASE_VERSION = "OB53"


def pad(text: bytes) -> bytes:
    """Add PKCS7 padding"""
    padding_length = AES.block_size - (len(text) % AES.block_size)
    padding = bytes([padding_length] * padding_length)
    return text + padding


def unpad(text: bytes) -> bytes:
    """Remove PKCS7 padding"""
    padding_length = text[-1]
    return text[:-padding_length]


def aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt with AES-CBC"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext)
    return aes.encrypt(padded)


def aes_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt with AES-CBC"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    decrypted = aes.decrypt(ciphertext)
    return unpad(decrypted)


async def get_player_info_ind(uid: str) -> dict:
    """
    Get REAL player information from Free Fire Indian server
    Returns: {success: bool, name: str, likes: int, level: int}
    """
    try:
        # Prepare request payload
        request_data = {
            "uid": uid,
            "platform": "android"
        }

        payload_bytes = json.dumps(request_data).encode('utf-8')
        encrypted_payload = aes_encrypt(MAIN_KEY, MAIN_IV, payload_bytes)

        headers = {
            "User-Agent": USER_AGENT,
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/octet-stream",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": RELEASE_VERSION,
        }

        # Try GetPlayerProfile endpoint
        url = f"{IND_SERVER}/GetPlayerProfile"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, data=encrypted_payload, headers=headers)

            if response.status_code == 200:
                # Decrypt response
                encrypted_response = response.content
                decrypted = aes_decrypt(MAIN_KEY, MAIN_IV, encrypted_response)
                data = json.loads(decrypted)

                return {
                    "success": True,
                    "name": data.get("nickname", f"Player-{uid[-4:]}"),
                    "likes": data.get("liked", 0),
                    "level": data.get("level", 1),
                    "uid": uid
                }
            else:
                # Fallback: Try alternative endpoint
                return await get_player_info_fallback(uid)

    except Exception as e:
        logger.error(f"Error fetching player info for {uid}: {e}")
        return await get_player_info_fallback(uid)


async def get_player_info_fallback(uid: str) -> dict:
    """
    Fallback method using public API or simple endpoint
    """
    try:
        # Try simple public endpoint without encryption
        url = f"{IND_SERVER}/social/profile/{uid}"

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("name", data.get("nickname", f"Player-{uid[-4:]}")),
                    "likes": data.get("likes", data.get("liked", 0)),
                    "level": data.get("level", 1),
                    "uid": uid
                }
    except:
        pass

    # Final fallback
    return {
        "success": False,
        "name": f"Player-{uid[-4:]}",
        "likes": 0,
        "level": 1,
        "uid": uid
    }


async def get_likes_count_ind(uid: str) -> int:
    """
    Get ONLY the likes count for a player
    """
    player_info = await get_player_info_ind(uid)
    return player_info.get("likes", 0)
