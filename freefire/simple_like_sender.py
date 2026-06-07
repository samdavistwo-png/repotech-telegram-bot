"""
Simple Like Sender - Alternative method using direct API calls
No auth server needed, uses guest accounts directly
"""

import httpx
import asyncio
import json
import base64
from Crypto.Cipher import AES
from ff_proto import freefire_pb2
from google.protobuf import json_format
from typing import Tuple, Dict

# Constants
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
RELEASE_VERSION = "OB53"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"

# Server URLs by region
REGION_SERVERS = {
    "IND": "https://client.ind.freefiremobile.com",
    "BR": "https://client.us.freefiremobile.com",
    "US": "https://client.us.freefiremobile.com",
    "SG": "https://client.sg.freefiremobile.com",
}


def pad(text: bytes) -> bytes:
    """Add PKCS7 padding"""
    padding_length = AES.block_size - (len(text) % AES.block_size)
    padding = bytes([padding_length] * padding_length)
    return text + padding


def aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt with AES-CBC"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext)
    return aes.encrypt(padded)


async def get_garena_token(uid: str, password: str) -> Tuple[str, str]:
    """
    Get access token from Garena OAuth
    Returns: (access_token, open_id)
    """
    payload = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret={CLIENT_SECRET}&client_id={CLIENT_ID}"

    headers = {
        'User-Agent': USER_AGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GARENA_TOKEN_URL, data=payload, headers=headers)
        data = response.json()

        access_token = data.get("access_token", "0")
        open_id = data.get("open_id", "0")

        if access_token == "0" or open_id == "0":
            raise ValueError("Failed to obtain Garena access token")

        return access_token, open_id


async def send_like_direct(guest_uid: str, guest_password: str, target_uid: str, region: str = "IND") -> Dict[str, any]:
    """
    Send a single like using guest account - Direct method without auth server

    Args:
        guest_uid: Guest account UID
        guest_password: Guest account password
        target_uid: Target player UID to receive like
        region: Server region (default: IND)

    Returns:
        dict: {"success": bool, "error": str or None}
    """
    try:
        # Step 1: Get Garena access token
        access_token, open_id = await get_garena_token(guest_uid, guest_password)

        # Step 2: Use access token as JWT (Free Fire accepts Garena tokens directly)
        jwt_token = access_token

        # Step 3: Get server URL for region
        server_url = REGION_SERVERS.get(region, REGION_SERVERS["IND"])

        # Step 4: Create like request protobuf
        like_req = {
            "a": target_uid,  # Target UID to like
            "b": "0"          # Unknown field, usually 0
        }

        # Serialize to protobuf (using generic message structure)
        like_proto = freefire_pb2.LoginReq()  # Reusing LoginReq structure
        like_json = json.dumps(like_req)
        json_format.ParseDict(json.loads(like_json), like_proto)
        serialized = like_proto.SerializeToString()

        # Step 5: Encrypt the payload
        encrypted_payload = aes_encrypt(MAIN_KEY, MAIN_IV, serialized)

        # Step 6: Send like request
        headers = {
            "User-Agent": USER_AGENT,
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/octet-stream",
            "Expect": "100-continue",
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": RELEASE_VERSION,
        }

        like_url = f"{server_url}/LikeProfile"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(like_url, data=encrypted_payload, headers=headers)
            response.raise_for_status()

            return {"success": True, "error": None}

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            return {"success": False, "error": "Free Fire server unavailable (503)"}
        else:
            return {"success": False, "error": f"HTTP {e.response.status_code}"}
    except ValueError as e:
        return {"success": False, "error": f"Auth failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def send_multiple_likes(guest_accounts: list, target_uid: str, max_concurrent: int = 20, region: str = "IND") -> Tuple[int, list]:
    """
    Send multiple likes using guest accounts pool

    Args:
        guest_accounts: List of dicts with 'uid' and 'password'
        target_uid: Target player UID
        max_concurrent: Max concurrent requests
        region: Server region

    Returns:
        Tuple of (successful_count, errors_list)
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def send_with_semaphore(guest):
        async with semaphore:
            return await send_like_direct(guest['uid'], guest['password'], target_uid, region)

    # Send all likes concurrently
    tasks = [send_with_semaphore(guest) for guest in guest_accounts]
    results = await asyncio.gather(*tasks)

    # Count successes and collect errors
    successful = sum(1 for r in results if r["success"])
    errors = [r["error"] for r in results if not r["success"]]

    return successful, errors


# Test function
async def test_send_like():
    """Test the like sending function"""
    # Example guest account (from the pool)
    test_guest = {
        'uid': '4104125669',
        'password': 'E5655A0D14EF812A908726152BDD38021BEF528801AA42B16CFA4ED67141C4CA'
    }

    # Test target UID (replace with real UID)
    test_target = '1234567890'

    print("Testing direct like sending...")
    result = await send_like_direct(test_guest['uid'], test_guest['password'], test_target)

    if result["success"]:
        print("✅ Like sent successfully!")
    else:
        print(f"❌ Failed: {result['error']}")

    return result


if __name__ == "__main__":
    asyncio.run(test_send_like())
