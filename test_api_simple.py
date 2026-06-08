#!/usr/bin/env python3
"""
Simple HL Gaming API test
"""

import urllib.request
import urllib.parse
import json

# Credentials from .env
USER_UID = "txnuOflAvIQxwFsfZ8GkTygDYcg2"
API_KEY = "jO6UCe7EARqYsxXkJSkwCweJ0T2ii3"

print("=" * 60)
print("🧪 TESTING HL GAMING LIKES API")
print("=" * 60)
print()

test_uid = "1810201201"

# Test likes sending
print("TESTING LIKES SENDING:")
print(f"Target UID: {test_uid}")
print(f"Amount: 100")
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

    print(f"URL: {url}")
    print()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    req = urllib.request.Request(full_url, headers=headers, method='GET')

    with urllib.request.urlopen(req, timeout=30) as response:
        print(f"✅ Status Code: {response.status}")
        data = json.loads(response.read().decode('utf-8'))
        print(f"✅ Response:")
        print(json.dumps(data, indent=2))
        print()
        print("✅ LIKES API WORKS!")

except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8') if e.fp else ''
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    print(f"❌ Response Body:")
    print(error_body)
    print()

    # Try to parse error response
    try:
        error_data = json.loads(error_body)
        print("❌ Parsed Error:")
        print(json.dumps(error_data, indent=2))
    except:
        print("(Could not parse as JSON)")

except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
