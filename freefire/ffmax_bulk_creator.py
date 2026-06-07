"""
Free Fire MAX Bulk Account Creator
Creates 100+ guest accounts named Sambots##1##, Sambots##2##, etc.
Supports both Free Fire and Free Fire MAX
"""

import json
import random
import string
import time
import urllib.request
import urllib.parse
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

# Free Fire Configuration
FF_REGISTER_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/register"
FF_CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
FF_CLIENT_ID = "100067"

# Free Fire MAX Configuration
FFMAX_REGISTER_URL = "https://ffmaxconnect.live.gop.garenanow.com/oauth/guest/register"
FFMAX_CLIENT_SECRET = "3ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e4"  # Different for MAX
FFMAX_CLIENT_ID = "100068"

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"


def generate_device_id() -> str:
    """Generate random device ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


def generate_android_id() -> str:
    """Generate random Android ID"""
    return ''.join(random.choices(string.hexdigits.lower(), k=16))


def create_guest_account(account_number: int, use_ffmax: bool = True) -> dict:
    """
    Create a single guest account

    Args:
        account_number: Account number for naming (Sambots##N##)
        use_ffmax: True for FF MAX, False for regular FF
    """
    try:
        device_id = generate_device_id()
        android_id = generate_android_id()

        # Choose FF or FF MAX configuration
        register_url = FFMAX_REGISTER_URL if use_ffmax else FF_REGISTER_URL
        client_id = FFMAX_CLIENT_ID if use_ffmax else FF_CLIENT_ID
        client_secret = FFMAX_CLIENT_SECRET if use_ffmax else FF_CLIENT_SECRET

        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
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

        form_data = '&'.join([f"{k}={v}" for k, v in payload.items()])
        form_data_bytes = form_data.encode('utf-8')

        req = urllib.request.Request(
            register_url,
            data=form_data_bytes,
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                if data.get("code") == 0 or "uid" in data:
                    uid = str(data.get("uid", data.get("open_id", "")))
                    password = data.get("password", "")

                    if uid and password:
                        return {
                            "success": True,
                            "uid": uid,
                            "password": password,
                            "account_name": f"Sambots##{account_number}##",
                            "type": "ffmax" if use_ffmax else "ff"
                        }

        return {"success": False, "error": "Registration failed"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def set_account_nickname(uid: str, password: str, nickname: str, use_ffmax: bool = True) -> bool:
    """
    Set nickname for a guest account

    Args:
        uid: Account UID
        password: Account password
        nickname: Desired nickname (e.g., "Sambots##1##")
        use_ffmax: True for FF MAX, False for regular FF
    """
    try:
        # First, get JWT token
        token_url = "https://ffmaxconnect.live.gop.garenanow.com/oauth/guest/token/grant" if use_ffmax else "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"

        client_id = FFMAX_CLIENT_ID if use_ffmax else FF_CLIENT_ID
        client_secret = FFMAX_CLIENT_SECRET if use_ffmax else FF_CLIENT_SECRET

        token_payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "guest_login",
            "uid": uid,
            "password": password
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        form_data = '&'.join([f"{k}={v}" for k, v in token_payload.items()])
        form_data_bytes = form_data.encode('utf-8')

        req = urllib.request.Request(
            token_url,
            data=form_data_bytes,
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                jwt_token = data.get("access_token", "")

                if jwt_token:
                    # Now set nickname using game API
                    server_url = "https://client.ind.ffmax.garenanow.com" if use_ffmax else "https://client.ind.freefiremobile.com"
                    nickname_url = f"{server_url}/SetNickname"

                    nickname_payload = json.dumps({"nickname": nickname}).encode('utf-8')

                    headers = {
                        "User-Agent": USER_AGENT,
                        "Authorization": f"Bearer {jwt_token}",
                        "Content-Type": "application/json"
                    }

                    req = urllib.request.Request(
                        nickname_url,
                        data=nickname_payload,
                        headers=headers,
                        method='POST'
                    )

                    with urllib.request.urlopen(req, timeout=15) as resp:
                        return resp.status in [200, 201, 204]

        return False

    except Exception as e:
        logger.debug(f"Failed to set nickname: {e}")
        return False


def create_bulk_accounts(count: int = 100, delay: float = 3.0, use_ffmax: bool = True) -> List[Dict]:
    """
    Create bulk guest accounts with Sambots naming

    Args:
        count: Number of accounts to create (default: 100)
        delay: Delay between creations to avoid rate limiting (default: 3s)
        use_ffmax: True for FF MAX, False for regular FF
    """
    accounts = []
    successful = 0
    failed = 0

    game_type = "Free Fire MAX" if use_ffmax else "Free Fire"

    print(f"\n{'='*70}")
    print(f"CREATING {count} {game_type.upper()} GUEST ACCOUNTS")
    print(f"{'='*70}")
    print(f"⏱️  Delay: {delay}s between accounts")
    print(f"🎮 Game: {game_type}")
    print(f"📝 Naming: Sambots##1## to Sambots##{count}##")
    print(f"\n📊 Progress:\n")

    for i in range(1, count + 1):
        print(f"[{i}/{count}] Creating Sambots##{i}##...", end=" ", flush=True)

        result = create_guest_account(i, use_ffmax)

        if result.get("success"):
            uid = result["uid"]
            password = result["password"]
            account_name = result["account_name"]

            # Try to set the nickname
            nickname_set = set_account_nickname(uid, password, account_name, use_ffmax)

            accounts.append({
                "uid": uid,
                "password": password,
                "name": account_name,
                "nickname_set": nickname_set,
                "type": result["type"]
            })
            successful += 1

            status = "✅ SUCCESS"
            if nickname_set:
                status += " + Nickname Set"

            print(status)

        else:
            failed += 1
            print(f"❌ FAILED: {result.get('error', 'Unknown')}")

        # Delay to avoid rate limiting
        if i < count:
            time.sleep(delay)

    print(f"\n{'='*70}")
    print(f"📊 SUMMARY:")
    print(f"   ✅ Successful: {successful}/{count}")
    print(f"   ❌ Failed: {failed}/{count}")
    print(f"   📈 Success Rate: {(successful/count)*100:.1f}%")
    print(f"{'='*70}\n")

    return accounts


def save_bulk_accounts(accounts: List[Dict], filename: str = "../freefire/sambots_accounts.json"):
    """Save bulk accounts to JSON file"""
    data = {
        "accounts": accounts,
        "created_at": datetime.now().isoformat(),
        "total_accounts": len(accounts),
        "naming_pattern": "Sambots##N##",
        "description": "Bulk guest accounts for Free Fire likes system"
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"💾 Saved {len(accounts)} accounts to {filename}")


if __name__ == "__main__":
    print("\n⚠️  BULK ACCOUNT CREATOR")
    print("This will create 100+ guest accounts named Sambots##1##, Sambots##2##, etc.")
    print("\nOptions:")
    print("  1. Free Fire MAX (India Server) - RECOMMENDED")
    print("  2. Free Fire Regular (India Server)")

    choice = input("\nSelect game type (1 or 2): ").strip()
    use_ffmax = choice != "2"

    try:
        count = int(input("How many accounts to create? (recommended: 100-150): "))
        delay = float(input("Delay between accounts in seconds? (recommended: 3-5): "))
    except ValueError:
        print("❌ Invalid input! Using defaults: 100 accounts, 3s delay")
        count = 100
        delay = 3.0

    print("\n⚠️  WARNING:")
    print("Creating many accounts may trigger anti-bot detection.")
    print("Recommended: 3-5 seconds delay between accounts.")

    proceed = input("\nProceed? (yes/no): ")

    if proceed.lower() in ['yes', 'y']:
        accounts = create_bulk_accounts(count, delay, use_ffmax)

        if accounts:
            save_bulk_accounts(accounts)
            print("\n✅ DONE!")
            print("\nNext steps:")
            print("  1. Update the likes engine to use these accounts")
            print("  2. Deploy to Railway")
            print("  3. Test with /likes command")
        else:
            print("\n❌ No accounts created!")
    else:
        print("Cancelled.")
