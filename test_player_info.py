"""
Test script to fetch player information
"""
import urllib.request
import urllib.parse
import json

def get_player_info(uid: str):
    """Get player info from Garena API"""

    print(f"\n🔍 Fetching player info for UID: {uid}\n")

    # Method 1: Garena antispam API
    try:
        print("📡 Trying Method 1: Garena antispam API...")
        url = "https://ff.garena.com/api/antispam/get_user_basic_info"
        payload = json.dumps({"uid": uid, "region": "IND"}).encode('utf-8')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("code") == 0:
                    user = data.get("data", {})
                    name = user.get("nickname", "")
                    likes = user.get("liked", 0)
                    level = user.get("level", 1)

                    if name:
                        print("✅ Method 1 SUCCESS!")
                        return {
                            "success": True,
                            "name": name,
                            "likes": likes,
                            "level": level,
                            "method": "Garena antispam API"
                        }

        print("❌ Method 1 failed - no data returned")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")

    # Method 2: FF.garena.com profile API
    try:
        print("\n📡 Trying Method 2: FF.garena.com profile API...")
        url = f"https://ff.garena.com/api/profile/{uid}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        req = urllib.request.Request(url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                name = data.get("nickname", data.get("name", ""))
                likes = data.get("liked", 0)
                level = data.get("level", 1)

                if name:
                    print("✅ Method 2 SUCCESS!")
                    return {
                        "success": True,
                        "name": name,
                        "likes": likes,
                        "level": level,
                        "method": "FF.garena.com profile API"
                    }

        print("❌ Method 2 failed - no data returned")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")

    # Method 3: Try alternative Free Fire API
    try:
        print("\n📡 Trying Method 3: Alternative FF API...")
        url = f"https://freefireinfo.site/api/info/sg/{uid}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        req = urllib.request.Request(url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                # Different API structures
                if "nickname" in data:
                    name = data.get("nickname", "")
                elif "name" in data:
                    name = data.get("name", "")
                elif "accountName" in data:
                    name = data.get("accountName", "")
                else:
                    name = ""

                likes = data.get("likes", data.get("liked", 0))
                level = data.get("level", 1)

                if name:
                    print("✅ Method 3 SUCCESS!")
                    return {
                        "success": True,
                        "name": name,
                        "likes": likes,
                        "level": level,
                        "method": "Alternative FF API"
                    }

        print("❌ Method 3 failed - no data returned")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")

    # All methods failed
    print("\n⚠️  All methods failed to fetch player info")
    return {
        "success": False,
        "name": f"FF-{uid[-6:]}",
        "likes": 0,
        "level": 1,
        "method": "Fallback (UID-based)"
    }

if __name__ == "__main__":
    uid = "1810201201"

    result = get_player_info(uid)

    print("\n" + "="*60)
    print("PLAYER INFORMATION")
    print("="*60)
    print(f"UID:          {uid}")
    print(f"In-Game Name: {result['name']}")
    print(f"Level:        {result['level']}")
    print(f"Current Likes: {result['likes']}")
    print(f"Data Source:  {result['method']}")
    print("="*60)

    if not result['success']:
        print("\n⚠️  WARNING: Could not fetch real player data from Garena APIs")
        print("This may indicate:")
        print("  • UID does not exist")
        print("  • Player has privacy settings enabled")
        print("  • Garena APIs are temporarily down")
