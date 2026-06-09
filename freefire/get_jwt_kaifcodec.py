"""
JWT Generation using kaifcodec's API approach
Uses our own deployed JWT generator API instead of broken ggblueshark server

This module provides a client for generating JWTs from guest account credentials.
It can work with:
1. Our own deployed JWT API (recommended)
2. kaifcodec's public endpoint (if available)
3. Local JWT generation (fallback)
"""

import httpx
import logging
from typing import Tuple, Optional
import os

logger = logging.getLogger(__name__)

# JWT API endpoints to try (in order of preference)
JWT_API_ENDPOINTS = [
    # Our own Railway deployment (will be available after deployment)
    os.getenv("JWT_API_URL", ""),  # Set via environment variable

    # Local development endpoint
    "http://localhost:3000/api/token",

    # Potential public deployments (update if kaifcodec provides public endpoint)
    "https://freefire-jwt-api.onrender.com/api/token",
    "https://ff-jwt-api.fly.dev/api/token",
]

# Filter out empty endpoints
JWT_API_ENDPOINTS = [e for e in JWT_API_ENDPOINTS if e]

async def create_jwt(uid: str, password: str) -> Tuple[str, str, str]:
    """
    Generate JWT using JWT API

    This function tries multiple JWT API endpoints to generate a valid JWT token
    from guest account credentials.

    Args:
        uid: Guest account UID
        password: Guest account password

    Returns:
        Tuple of (jwt_token, region, server_url)
        Returns ("", "", "") if all endpoints fail
    """

    if not JWT_API_ENDPOINTS:
        logger.error("❌ No JWT API endpoints configured!")
        logger.error("💡 Set JWT_API_URL environment variable or deploy JWT API")
        return "", "", ""

    # Try each endpoint in order
    for endpoint in JWT_API_ENDPOINTS:
        try:
            logger.debug(f"🔗 Trying JWT API: {endpoint}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try POST request (preferred)
                response = await client.post(
                    endpoint,
                    json={"uid": uid, "password": password},
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    jwt_token = data.get("token", "")
                    region = data.get("lockRegion", "IND")
                    server_url = data.get("serverUrl", "https://client.ind.freefiremobile.com")

                    if jwt_token:
                        logger.info(f"✅ JWT obtained from {endpoint}")
                        logger.debug(f"   JWT: {jwt_token[:30]}...{jwt_token[-20:]}")
                        return jwt_token, region, server_url
                    else:
                        logger.warning(f"⚠️  JWT API returned empty token: {data}")
                else:
                    logger.debug(f"⚠️  Endpoint {endpoint} returned {response.status_code}")

        except httpx.ConnectError:
            logger.debug(f"⚠️  Cannot connect to {endpoint} (may not be running)")
        except httpx.TimeoutException:
            logger.warning(f"⚠️  Timeout connecting to {endpoint}")
        except Exception as e:
            logger.debug(f"⚠️  Endpoint {endpoint} failed: {type(e).__name__}: {e}")
            continue

    logger.error("❌ All JWT API endpoints failed")
    logger.error("💡 Solutions:")
    logger.error("   1. Deploy JWT API: cd jwt_api && uvicorn main:app --port 3000")
    logger.error("   2. Set JWT_API_URL environment variable")
    logger.error("   3. Deploy to Railway/Render (see deployment docs)")

    return "", "", ""

async def create_jwt_local(uid: str, password: str) -> Tuple[str, str, str]:
    """
    Generate JWT locally without API (fallback method)

    This is a fallback that can be used if the JWT API is not available.
    It replicates the JWT generation logic locally.

    Args:
        uid: Guest account UID
        password: Guest account password

    Returns:
        Tuple of (jwt_token, region, server_url)
    """
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        import base64
        from freefire.ff_proto import freefire_pb2

        logger.info("🔧 Using local JWT generation (fallback)")

        # Step 1: Get OAuth token
        OAUTH_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
        USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"

        payload = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }

        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        form_data = "&".join([f"{k}={v}" for k, v in payload.items()])

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OAUTH_URL, data=form_data, headers=headers)

            if response.status_code != 200:
                logger.error(f"❌ OAuth failed: {response.status_code}")
                return "", "", ""

            data = response.json()
            access_token = data.get("access_token", "")
            open_id = data.get("open_id", "")

            if not access_token or not open_id:
                logger.error(f"❌ OAuth response missing tokens")
                return "", "", ""

        # Step 2: Create JWT from OAuth token
        MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
        MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")

        login_req = freefire_pb2.LoginReq()
        login_req.open_id = open_id
        login_req.login_token = access_token
        login_req.open_id_type = "2"
        login_req.orign_platform_type = "1"

        serialized = login_req.SerializeToString()
        cipher = AES.new(MAIN_KEY, AES.MODE_CBC, MAIN_IV)
        encrypted = cipher.encrypt(pad(serialized, AES.block_size))
        jwt_token = base64.b64encode(encrypted).decode()

        logger.info(f"✅ Local JWT generated successfully")
        return jwt_token, "IND", "https://client.ind.freefiremobile.com"

    except ImportError as e:
        logger.error(f"❌ Missing dependency for local JWT generation: {e}")
        logger.error("💡 Install: pip install pycryptodome")
        return "", "", ""
    except Exception as e:
        logger.error(f"❌ Local JWT generation failed: {e}")
        return "", "", ""

async def create_jwt_with_fallback(uid: str, password: str) -> Tuple[str, str, str]:
    """
    Generate JWT with automatic fallback

    Tries JWT API first, then falls back to local generation if needed.

    Args:
        uid: Guest account UID
        password: Guest account password

    Returns:
        Tuple of (jwt_token, region, server_url)
    """
    # Try JWT API first
    jwt_token, region, server_url = await create_jwt(uid, password)

    if jwt_token:
        return jwt_token, region, server_url

    # Fallback to local generation
    logger.warning("⚠️  JWT API unavailable, trying local generation...")
    return await create_jwt_local(uid, password)

# Main export function (use this in guest_likes_engine.py)
create_jwt_token = create_jwt_with_fallback

if __name__ == "__main__":
    # Quick test
    import asyncio

    async def test():
        print("🧪 Testing JWT API client...")
        print(f"📋 Configured endpoints: {len(JWT_API_ENDPOINTS)}")
        for i, endpoint in enumerate(JWT_API_ENDPOINTS, 1):
            print(f"   {i}. {endpoint}")
        print()

        # Test with dummy credentials
        jwt, region, server = await create_jwt("test_uid", "test_password")

        if jwt:
            print(f"✅ JWT generated successfully!")
            print(f"   JWT: {jwt[:30]}...{jwt[-20:]}")
            print(f"   Region: {region}")
            print(f"   Server: {server}")
        else:
            print(f"❌ JWT generation failed")
            print(f"💡 Make sure JWT API is running or deploy it first")

    asyncio.run(test())
