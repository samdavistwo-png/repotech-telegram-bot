"""
Free Fire Authentication Server
Replaces loginbp.ggblueshark.com/MajorLogin endpoint

This server handles JWT generation for Free Fire game authentication.
It acts as a proxy between the Telegram bot and Free Fire game servers.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from Crypto.Cipher import AES
import httpx
import base64
import sys
import logging
from typing import Tuple

# Add freefire module to path
sys.path.insert(0, './freefire')

from ff_proto import freefire_pb2
from google.protobuf import json_format

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Free Fire Auth Server",
    description="Authentication proxy for Free Fire API",
    version="1.0.0"
)

# Encryption keys (keep these secret!)
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

# Garena OAuth endpoint (official)
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"

# User agent for requests
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"


def unpad(data: bytes) -> bytes:
    """Remove PKCS7 padding from decrypted data"""
    padding_length = data[-1]
    return data[:-padding_length]


def pad(text: bytes) -> bytes:
    """Add PKCS7 padding to data before encryption"""
    padding_length = AES.block_size - (len(text) % AES.block_size)
    padding = bytes([padding_length] * padding_length)
    return text + padding


def aes_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt AES-CBC encrypted data"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    plaintext = aes.decrypt(ciphertext)
    return unpad(plaintext)


def aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt data with AES-CBC"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext)
    return aes.encrypt(padded)


async def verify_garena_token(access_token: str, open_id: str) -> bool:
    """
    Verify token with Garena (optional validation)
    Returns True if token appears valid
    """
    # For now, we trust the token since it came from Garena OAuth
    # In production, you could add additional validation here
    if not access_token or access_token == "0":
        return False
    if not open_id or open_id == "0":
        return False
    return True


def determine_region_and_server(open_id: str) -> Tuple[str, str]:
    """
    Determine region and server URL based on open_id

    In production, you would have a more sophisticated mapping.
    For now, defaulting to IND (India) server.
    """
    # You can expand this logic based on open_id patterns
    # Different regions may have different open_id ranges

    region_mapping = {
        "IND": "https://client.ind.freefiremobile.com",
        "BR": "https://client.us.freefiremobile.com",
        "US": "https://client.us.freefiremobile.com",
        "SG": "https://client.sg.freefiremobile.com",
        # Add more as needed
    }

    # Default to IND for now
    # You could implement logic to detect region from open_id
    default_region = "IND"
    default_server = region_mapping.get(default_region, "https://client.ind.freefiremobile.com")

    return default_region, default_server


@app.post("/MajorLogin")
async def major_login(request: Request):
    """
    Handle MajorLogin requests
    This is the core endpoint that replaces ggblueshark.com/MajorLogin

    Flow:
    1. Receive encrypted LoginReq from bot
    2. Decrypt with AES
    3. Parse protobuf
    4. Validate token
    5. Determine region
    6. Build LoginRes with JWT
    7. Encrypt response
    8. Return to bot
    """
    client_ip = request.client.host

    try:
        # 1. Read encrypted request body
        encrypted_body = await request.body()
        logger.info(f"[{client_ip}] Received MajorLogin request ({len(encrypted_body)} bytes)")

        # 2. Decrypt with AES
        try:
            decrypted = aes_decrypt(MAIN_KEY, MAIN_IV, encrypted_body)
        except Exception as e:
            logger.error(f"[{client_ip}] Decryption failed: {e}")
            return Response(
                content=b"Invalid encryption",
                status_code=400,
                media_type="text/plain"
            )

        # 3. Parse protobuf LoginReq
        try:
            login_req = freefire_pb2.LoginReq()
            login_req.ParseFromString(decrypted)
        except Exception as e:
            logger.error(f"[{client_ip}] Protobuf parsing failed: {e}")
            return Response(
                content=b"Invalid protobuf data",
                status_code=400,
                media_type="text/plain"
            )

        # Extract credentials
        open_id = login_req.open_id
        login_token = login_req.login_token

        logger.info(f"[{client_ip}] Login request for open_id: {open_id[:10]}...")

        # 4. Validate token
        if not await verify_garena_token(login_token, open_id):
            logger.warning(f"[{client_ip}] Invalid token")
            return Response(
                content=b"Invalid token",
                status_code=401,
                media_type="text/plain"
            )

        # 5. Determine region and server
        region, server_url = determine_region_and_server(open_id)
        logger.info(f"[{client_ip}] Assigned region: {region}, server: {server_url}")

        # 6. Generate JWT (use access token as JWT for now)
        # In a more sophisticated implementation, you could:
        # - Generate your own JWT with expiration
        # - Cache JWTs to reduce processing
        # - Add additional claims
        jwt_token = login_token

        # 7. Build LoginRes protobuf
        login_res = freefire_pb2.LoginRes()
        login_res.token = jwt_token
        login_res.lockRegion = region
        login_res.serverUrl = server_url

        # 8. Serialize to bytes
        response_data = login_res.SerializeToString()

        # 9. Encrypt response
        encrypted_response = aes_encrypt(MAIN_KEY, MAIN_IV, response_data)

        logger.info(f"[{client_ip}] Successfully generated JWT for {open_id[:10]}...")

        # 10. Return encrypted protobuf
        return Response(
            content=encrypted_response,
            media_type="application/octet-stream"
        )

    except Exception as e:
        logger.error(f"[{client_ip}] Unexpected error: {e}", exc_info=True)
        return Response(
            content=b"Internal Server Error",
            status_code=500,
            media_type="text/plain"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "service": "Free Fire Auth Server",
        "version": "1.0.0"
    }


@app.get("/stats")
async def stats():
    """Basic statistics endpoint"""
    # In production, you could track:
    # - Total requests
    # - Success rate
    # - Average response time
    # - Active regions
    return {
        "service": "Free Fire Auth Server",
        "status": "operational",
        "supported_regions": ["IND", "BR", "US", "SG"],
        "endpoints": {
            "auth": "/MajorLogin",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Free Fire Authentication Server",
        "version": "1.0.0",
        "description": "Proxy authentication server for Free Fire API",
        "endpoints": {
            "authentication": "POST /MajorLogin",
            "health_check": "GET /health",
            "statistics": "GET /stats"
        },
        "status": "operational"
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": ["/MajorLogin", "/health", "/stats", "/"]
        }
    )


if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment or use 8000
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting Free Fire Auth Server on port {port}...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
