"""
Temporary Guest Account Creator
Creates disposable Free Fire guest accounts on demand
"""

import httpx
import asyncio
import json
import base64
import random
import string
from typing import Dict, List

# Garena API endpoints
GUEST_REGISTER_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/register"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"


def generate_device_id() -> str:
    """Generate a random device ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


def generate_android_id() -> str:
    """Generate a random Android ID"""
    return ''.join(random.choices(string.hexdigits.lower(), k=16))


async def create_temp_guest_account() -> Dict:
    """
    Create a temporary Free Fire guest account

    Returns:
        dict: {"success": bool, "uid": str, "password": str, "token": str}
    """
    try:
        # Generate unique identifiers
        device_id = generate_device_id()
        android_id = generate_android_id()

        # Prepare registration payload
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "device_id": device_id,
            "android_id": android_id,
            "app_version": "1.99.3",
            "platform": "android"
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        # URL-encode payload
        form_data = '&'.join([f"{k}={v}" for k, v in payload.items()])

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                GUEST_REGISTER_URL,
                data=form_data,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == 0 or "uid" in data:
                    return {
                        "success": True,
                        "uid": str(data.get("uid", data.get("open_id", ""))),
                        "password": data.get("password", ""),
                        "token": data.get("access_token", "")
                    }

        return {"success": False, "error": "Registration failed"}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def create_multiple_guest_accounts(count: int) -> List[Dict]:
    """
    Create multiple temporary guest accounts concurrently

    Args:
        count: Number of accounts to create

    Returns:
        List of account dicts with uid and password
    """
    tasks = [create_temp_guest_account() for _ in range(count)]
    results = await asyncio.gather(*tasks)

    # Filter successful accounts
    accounts = [
        {"uid": r["uid"], "password": r["password"]}
        for r in results if r.get("success") and r.get("uid")
    ]

    return accounts


async def get_guest_accounts_pool(needed: int = 100) -> List[Dict]:
    """
    Get a pool of guest accounts
    First tries existing accounts, then creates temporary ones if needed

    Args:
        needed: Number of accounts needed

    Returns:
        List of account dicts
    """
    import os

    # Try to load existing accounts first
    accounts_file = os.path.join(os.path.dirname(__file__), 'accounts.json')
    existing_accounts = []

    try:
        with open(accounts_file, 'r') as f:
            data = json.load(f)
            existing_accounts = data.get('guest_accounts', [])
    except:
        pass

    # If we have enough existing accounts, use them
    if len(existing_accounts) >= needed:
        return existing_accounts[:needed]

    # Otherwise, create temporary accounts
    print(f"Creating {needed} temporary guest accounts...")
    temp_accounts = await create_multiple_guest_accounts(needed)

    # Combine existing + temp
    all_accounts = existing_accounts + temp_accounts
    return all_accounts[:needed]


# Test function
async def test_create_account():
    """Test creating a single account"""
    print("Creating temporary guest account...")
    result = await create_temp_guest_account()

    if result.get("success"):
        print(f"✅ Account created!")
        print(f"   UID: {result['uid']}")
        print(f"   Password: {result['password'][:20]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_create_account())
