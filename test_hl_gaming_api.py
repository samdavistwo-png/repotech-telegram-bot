#!/usr/bin/env python3
"""
Test HL Gaming API to diagnose "Bad Request" error
"""

import os
import urllib.request
import urllib.parse
import json
from dotenv import load_dotenv

load_dotenv()

USER_UID = os.getenv("HL_GAMING_USERUID", "")
API_KEY = os.getenv("HL_GAMING_API_KEY", "")

print("=" * 60)
print("🧪 TESTING HL GAMING API")
print("=" * 60)
print()

# Test credentials
print("1. CREDENTIALS CHECK:")
print(f"   USER_UID: {USER_UID[:10]}..." if USER_UID else "   USER_UID: NOT SET")
print(f"   API_KEY: {API_KEY[:10]}..." if API_KEY else "   API_KEY: NOT SET")
print()

if not USER_UID or not API_KEY:
    print("❌ CREDENTIALS NOT CONFIGURED!")
    print("   Add credentials to .env file:")
    print("   HL_GAMING_USERUID=your_uid_here")
    print("   HL_GAMING_API_KEY=your_key_here")
    exit(1)

# Test player info API
print("2. TESTING PLAYER INFO API:")
test_uid = "1810201201"
print(f"   Target UID: {test_uid}")
print()

try:
    params = {
        'sectionName': 'AllData',
        'PlayerUid': test_uid,
        'region': 'ind',
        'useruid': USER_UID,
        'api': API_KEY
    }

    url = "https://proapis.hlgamingofficial.com/main/games/freefire/account/api"
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    print(f"   URL: {url}")
    print(f"   Params: {params}")
    print()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    req = urllib.request.Request(full_url, headers=headers, method='GET')

    with urllib.request.urlopen(req, timeout=15) as response:
        print(f"   ✅ Status Code: {response.status}")
        data = json.loads(response.read().decode('utf-8'))
        print(f"   ✅ Response: {json.dumps(data, indent=2)}")
        print()

        account_info = data.get('AccountInfo', {})
        nickname = account_info.get('nickname', account_info.get('name', ''))
        print(f"   ✅ Player Name: {nickname}")
        print()

except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8') if e.fp else ''
    print(f"   ❌ HTTP Error {e.code}: {e.reason}")
    print(f"   ❌ Response: {error_body}")
    print()

except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    print()

# Test likes API
print("3. TESTING LIKES SENDING API:")
print(f"   Target UID: {test_uid}")
print(f"   Amount: 100")
print()

try:
    params = {
        'targetUid': test_uid,
        'amount': '100',
        'region': 'ind',
        'useruid': USER_UID,
        'api': API_KEY
    }

    url = "https://proapis.hlgamingofficial.com/main/games/freefire/likes/api"
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    print(f"   URL: {url}")
    print(f"   Params: {params}")
    print()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    req = urllib.request.Request(full_url, headers=headers, method='GET')

    with urllib.request.urlopen(req, timeout=30) as response:
        print(f"   ✅ Status Code: {response.status}")
        data = json.loads(response.read().decode('utf-8'))
        print(f"   ✅ Response: {json.dumps(data, indent=2)}")
        print()

except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8') if e.fp else ''
    print(f"   ❌ HTTP Error {e.code}: {e.reason}")
    print(f"   ❌ Response: {error_body}")
    print()

    # Try to parse error response
    try:
        error_data = json.loads(error_body)
        print(f"   ❌ Error Details: {json.dumps(error_data, indent=2)}")
    except:
        pass

except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    print()

print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
