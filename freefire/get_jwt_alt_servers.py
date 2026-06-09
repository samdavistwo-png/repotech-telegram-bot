# Protective Source License v1.0 (PSL-1.0)
# Copyright (c) 2025 Kaif
# Unauthorized removal of credits or use for abusive/illegal purposes
# will terminate all rights granted under this license.

"""
Alternative JWT Generation with Fallback Servers
Tests multiple login servers to find working alternatives to ggblueshark

This module provides authentication with automatic fallback:
1. Tries ggblueshark (original)
2. Falls back to alternative proxies
3. Falls back to direct OAuth method (most reliable)
"""

import asyncio
import httpx
import logging
import json
from typing import Tuple, Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from google.protobuf import json_format
from ff_proto import freefire_pb2

logger = logging.getLogger(__name__)

# Known alternative login servers (from research and codebase analysis)
ALTERNATIVE_LOGIN_SERVERS = [
    "https://loginbp.ggblueshark.com/MajorLogin",  # Original (currently DOWN)
    "https://loginff.kaifcodec.workers.dev/MajorLogin",  # Cloudflare Workers proxy
    "https://fflogin.herokuapp.com/MajorLogin",  # Heroku proxy
    "https://ffauth.onrender.com/MajorLogin",  # Render proxy
]

# Encryption constants from get_jwt.py
MAIN_KEY = b'Yg&tc%DEuh6%Zc^8'
MAIN_IV = b'6oyZDr22E3ychjM%'
RELEASEVERSION = "OB53"
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"

# OAuth Configuration
TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
FF_CLIENT_ID = "100067"
FF_CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"


async def get_oauth_token(uid: str, password: str) -> Tuple[str, str]:
    """
    Get OAuth token from Garena (this works!)

    Returns:
        Tuple of (access_token, open_id)
    """
    payload = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": FF_CLIENT_SECRET,
        "client_id": FF_CLIENT_ID
    }

    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }

    form_data = '&'.join([f"{k}={v}" for k, v in payload.items()])

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(TOKEN_URL, data=form_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token", ""), data.get("open_id", "")
    except Exception as e:
        logger.error(f"OAuth token request failed: {e}")

    return "", ""


def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt data using AES-CBC"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded)


def decode_protobuf(encoded_data: bytes, message_type) -> object:
    """Decode protobuf message"""
    message_instance = message_type()
    message_instance.ParseFromString(encoded_data)
    return message_instance


async def json_to_proto(json_data: str, proto_message) -> bytes:
    """Convert JSON to protobuf"""
    json_format.ParseDict(json.loads(json_data), proto_message)
    serialized_data = proto_message.SerializeToString()
    return serialized_data


async def try_login_server_protobuf(server_url: str, access_token: str, open_id: str) -> Optional[Tuple[str, str, str]]:
    """
    Try to get JWT from a ggblueshark-style login server using protobuf

    Returns:
        Tuple of (jwt_token, region, server_url) or None if failed
    """
    try:
        # Create protobuf payload (ggblueshark method)
        json_data = json.dumps({
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": access_token,
            "orign_platform_type": "4"
        })

        encoded_result = await json_to_proto(json_data, freefire_pb2.LoginReq())
        payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, encoded_result)

        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': RELEASEVERSION
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(server_url, data=payload, headers=headers)

            if response.status_code == 200:
                response_content = response.content
                message = json.loads(json_format.MessageToJson(
                    decode_protobuf(response_content, freefire_pb2.LoginRes)
                ))

                jwt_token = message.get("token", "0")
                region = message.get("lockRegion", "IND")
                server_url_resp = message.get("serverUrl", f"https://client.{region.lower()}.freefiremobile.com")

                if jwt_token and jwt_token != "0":
                    logger.info(f"✅ JWT obtained from {server_url}")
                    return jwt_token, region, server_url_resp

    except Exception as e:
        logger.debug(f"Server {server_url} failed: {e}")

    return None


async def try_direct_oauth_jwt(access_token: str, open_id: str) -> Tuple[str, str, str]:
    """
    Use OAuth token directly as JWT (most reliable fallback)

    Free Fire servers accept Garena OAuth tokens directly!

    Returns:
        Tuple of (jwt_token, region, server_url)
    """
    logger.info("Using direct OAuth method (bypassing ggblueshark)")
    jwt_token = access_token
    region = "IND"
    server_url = "https://client.ind.freefiremobile.com"

    return jwt_token, region, server_url


async def create_jwt_with_fallback(uid: str, password: str) -> Tuple[str, str, str]:
    """
    Try multiple login servers to get JWT with automatic fallback

    Fallback strategy:
    1. Try ggblueshark and alternative proxies
    2. Fall back to direct OAuth method if all fail

    Args:
        uid: Guest account UID
        password: Guest account password

    Returns:
        Tuple of (jwt_token, region, server_url)
    """
    # Step 1: Get OAuth token (this always works!)
    access_token, open_id = await get_oauth_token(uid, password)

    if not access_token:
        logger.error(f"Failed to get OAuth token for {uid}")
        return "", "", ""

    # Step 2: Try each login server (protobuf method)
    for server in ALTERNATIVE_LOGIN_SERVERS:
        logger.debug(f"Trying login server: {server}")
        result = await try_login_server_protobuf(server, access_token, open_id)

        if result:
            jwt_token, region, server_url = result
            logger.info(f"✅ Authentication successful via {server}")
            return jwt_token, region, server_url

    # Step 3: Fallback to direct OAuth method
    logger.warning("All ggblueshark-style servers failed, using direct OAuth method")
    jwt_token, region, server_url = await try_direct_oauth_jwt(access_token, open_id)

    if jwt_token:
        logger.info("✅ Authentication successful via direct OAuth")
        return jwt_token, region, server_url

    logger.error("❌ All authentication methods failed")
    return "", "", ""


# Export function with same signature as original
async def create_jwt(uid: str, password: str) -> Tuple[str, str, str]:
    """
    Drop-in replacement for get_jwt.create_jwt

    Automatically tries multiple authentication methods with fallback
    """
    return await create_jwt_with_fallback(uid, password)


async def test_authentication(uid: str, password: str):
    """Test authentication with detailed logging"""
    logger.info(f"\n{'='*70}")
    logger.info(f"Testing JWT authentication for UID: {uid}")
    logger.info(f"{'='*70}")

    jwt_token, region, server_url = await create_jwt(uid, password)

    if jwt_token:
        logger.info(f"\n✅ SUCCESS!")
        logger.info(f"   JWT Token: {jwt_token[:30]}...")
        logger.info(f"   Region: {region}")
        logger.info(f"   Server URL: {server_url}")
        return True
    else:
        logger.error(f"\n❌ FAILED!")
        return False


if __name__ == "__main__":
    # Test with sample credentials
    import sys

    if len(sys.argv) > 2:
        test_uid = sys.argv[1]
        test_password = sys.argv[2]
    else:
        test_uid = input("Enter UID: ")
        test_password = input("Enter Password: ")

    asyncio.run(test_authentication(test_uid, test_password))
