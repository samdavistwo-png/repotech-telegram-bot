"""
Free Fire JWT Generator API
Based on kaifcodec's freefire-jwt-generator-api
Deploys as separate service on Railway/Modal/Render
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import logging
import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# Add parent directory to path to import freefire module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freefire.ff_proto import freefire_pb2

app = FastAPI(title="Free Fire JWT API", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants from kaifcodec's settings.py
MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")  # Yg&tc%DEuh6%Zc^8
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")   # 6oyZDr22E3ychjM%
OAUTH_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
RELEASE_VERSION = "OB53"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"

class TokenRequest(BaseModel):
    uid: str
    password: str

class TokenResponse(BaseModel):
    token: str
    lockRegion: str
    serverUrl: str
    success: bool
    message: str = ""

async def get_oauth_token(uid: str, password: str) -> tuple:
    """
    Step 1: Get OAuth access token from Garena

    This uses the same OAuth endpoint that the official Free Fire client uses
    for guest account authentication.
    """
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

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OAUTH_URL, data=form_data, headers=headers)

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token", "")
                open_id = data.get("open_id", "")

                if access_token and open_id:
                    logger.info(f"✅ OAuth token obtained for uid={uid}")
                    return access_token, open_id
                else:
                    logger.error(f"❌ OAuth response missing tokens: {data}")
            else:
                logger.error(f"❌ OAuth request failed: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"❌ OAuth request exception: {e}")

    return "", ""

def create_jwt_from_oauth(access_token: str, open_id: str) -> tuple:
    """
    Step 2: Transform OAuth token to JWT using protobuf + AES encryption

    This mimics what the official Free Fire client does:
    1. Creates a LoginReq protobuf message with OAuth credentials
    2. Serializes the protobuf to binary
    3. Encrypts with AES-128-CBC using Free Fire's encryption keys
    4. Base64 encodes the result

    The encrypted token can then be used for Free Fire API requests.
    """

    try:
        # Create protobuf message (using our existing freefire_pb2)
        login_req = freefire_pb2.LoginReq()
        login_req.open_id = open_id
        login_req.login_token = access_token
        login_req.open_id_type = "2"  # Guest account type
        login_req.orign_platform_type = "1"  # Android platform

        # Serialize protobuf to binary
        serialized = login_req.SerializeToString()
        logger.debug(f"Protobuf serialized: {len(serialized)} bytes")

        # Encrypt with AES-128-CBC
        cipher = AES.new(MAIN_KEY, AES.MODE_CBC, MAIN_IV)
        encrypted = cipher.encrypt(pad(serialized, AES.block_size))
        encoded = base64.b64encode(encrypted).decode()

        logger.info(f"✅ JWT created: {len(encoded)} chars")

        # Return JWT token with default region settings
        # The actual Free Fire server would be determined by the client
        return encoded, "IND", "https://client.ind.freefiremobile.com"

    except Exception as e:
        logger.error(f"❌ JWT creation failed: {e}")
        return "", "", ""

@app.get("/api/token")
async def get_token_get(uid: str, password: str):
    """GET endpoint for quick testing"""
    return await generate_token(uid, password)

@app.post("/api/token")
async def get_token_post(request: TokenRequest):
    """POST endpoint (preferred)"""
    return await generate_token(request.uid, request.password)

async def generate_token(uid: str, password: str):
    """
    Generate JWT from guest credentials

    This is the main API endpoint that:
    1. Gets OAuth token from Garena
    2. Transforms it to JWT format
    3. Returns the JWT ready for Free Fire API calls
    """
    try:
        logger.info(f"🔑 Generating JWT for uid={uid}")

        # Step 1: Get OAuth token
        access_token, open_id = await get_oauth_token(uid, password)

        if not access_token:
            logger.error(f"❌ Failed to get OAuth token for uid={uid}")
            raise HTTPException(
                status_code=401,
                detail="Failed to authenticate with Garena OAuth. Check credentials."
            )

        # Step 2: Transform to JWT
        jwt_token, region, server_url = create_jwt_from_oauth(access_token, open_id)

        if not jwt_token:
            logger.error(f"❌ Failed to create JWT for uid={uid}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate JWT token"
            )

        logger.info(f"✅ JWT generated successfully for uid={uid}")

        return TokenResponse(
            token=jwt_token,
            lockRegion=region,
            serverUrl=server_url,
            success=True,
            message="JWT token generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ JWT generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "freefire-jwt-api",
        "version": "1.0.0",
        "based_on": "kaifcodec/freefire-jwt-generator-api"
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Free Fire JWT Generator API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/token": "Generate JWT (body: {uid, password})",
            "GET /api/token": "Generate JWT (params: ?uid=X&password=Y)",
            "GET /health": "Health check"
        },
        "based_on": "https://github.com/kaifcodec/freefire-jwt-generator-api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
