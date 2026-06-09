# Protective Source License v1.0 (PSL-1.0)
# Copyright (c) 2025 Kaif
# Unauthorized removal of credits or use for abusive/illegal purposes
# will terminate all rights granted under this license.

"""
Direct OAuth JWT - Bypasses ggblueshark completely
Uses Garena OAuth access tokens directly as JWTs

This module provides authentication that works even when ggblueshark.com is down.
It uses the Garena OAuth token directly as the JWT, which Free Fire servers accept.
"""

import httpx
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# OAuth Configuration
TOKEN_URL_FF = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
FF_CLIENT_ID = "100067"
FF_CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"


async def get_access_token(uid: str, password: str) -> Tuple[str, str]:
    """
    Get Garena OAuth access token

    This endpoint is UP and working (confirmed)!

    Args:
        uid: Guest account UID
        password: Guest account password (hex-encoded)

    Returns:
        Tuple of (access_token, open_id)
        Returns ("", "") if authentication fails
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
        'User-Agent': USER_AGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }

    # Convert payload to form-encoded string
    form_data = '&'.join([f"{k}={v}" for k, v in payload.items()])

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(TOKEN_URL_FF, data=form_data, headers=headers)

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token", "")
                open_id = data.get("open_id", "")

                if access_token and access_token != "0":
                    logger.info(f"OAuth token obtained for guest {uid}")
                    return access_token, open_id
                else:
                    logger.warning(f"OAuth token request returned invalid token for guest {uid}")
                    return "", ""
            else:
                logger.error(f"OAuth token failed for guest {uid}: HTTP {response.status_code}")
                return "", ""

    except Exception as e:
        logger.error(f"OAuth token request exception for guest {uid}: {e}")
        return "", ""


async def create_jwt_direct(uid: str, password: str) -> Tuple[str, str, str]:
    """
    Create JWT by using OAuth token directly (NO ggblueshark needed)

    This method bypasses the ggblueshark login server entirely.
    Free Fire servers accept Garena OAuth tokens as valid JWTs!

    Args:
        uid: Guest account UID
        password: Guest account password (hex-encoded)

    Returns:
        Tuple of (jwt_token, region, server_url)
        Returns ("", "", "") if authentication fails
    """
    # Get OAuth access token (this server is UP)
    access_token, open_id = await get_access_token(uid, password)

    if not access_token:
        logger.error(f"Failed to get OAuth token for {uid}")
        return "", "", ""

    # Use OAuth token DIRECTLY as JWT
    # Free Fire servers accept Garena OAuth tokens!
    jwt_token = access_token
    region = "IND"  # Default region
    server_url = "https://client.ind.freefiremobile.com"

    logger.info(f"Direct JWT created for guest {uid} (bypassed ggblueshark)")

    return jwt_token, region, server_url


# Fallback servers if IND is down
FALLBACK_SERVERS = [
    "https://client.ind.freefiremobile.com",
    "https://client.us.freefiremobile.com",
    "https://client.sg.freefiremobile.com",
    "https://client.ind.ffmax.garenanow.com",
]


async def find_working_server() -> str:
    """
    Find a working Free Fire server from the fallback list

    Returns:
        URL of first working server, or IND server as default
    """
    for server in FALLBACK_SERVERS:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try a HEAD request to check server status
                await client.head(f"{server}/", timeout=5.0)
                logger.info(f"Found working server: {server}")
                return server
        except:
            continue

    # Default to IND if all fail
    logger.warning("All servers unreachable, defaulting to IND")
    return "https://client.ind.freefiremobile.com"


async def check_oauth_endpoint() -> bool:
    """
    Check if Garena OAuth endpoint is accessible

    Returns:
        True if endpoint is up, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Send a test request
            response = await client.post(
                TOKEN_URL_FF,
                data="uid=test&password=test&response_type=token&client_type=2&client_secret={FF_CLIENT_SECRET}&client_id={FF_CLIENT_ID}",
                headers={
                    'User-Agent': USER_AGENT,
                    'Content-Type': "application/x-www-form-urlencoded"
                },
                timeout=5.0
            )

            # 200 means endpoint is up (even if credentials are invalid)
            # 405 Method Not Allowed is also OK (means POST is accepted but we used wrong method)
            if response.status_code in [200, 405]:
                logger.info("OAuth endpoint is UP")
                return True
            else:
                logger.warning(f"OAuth endpoint returned HTTP {response.status_code}")
                return False

    except Exception as e:
        logger.error(f"OAuth endpoint check failed: {e}")
        return False
