"""Test FF MAX player info with urllib (no dependencies)"""
import urllib.request
import json


def test_all_apis(uid: str):
    """Test all player info APIs"""

    print(f"\n{'='*70}")
    print(f"FETCHING PLAYER INFO FOR UID: {uid}")
    print(f"{'='*70}\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Method 1: FF MAX Garena antispam API
    print("📡 Method 1: FF MAX Garena antispam API...")
    try:
        url = "https://ffmax.garena.com/api/antispam/get_user_basic_info"
        payload = json.dumps({"uid": uid, "region": "IND"}).encode('utf-8')

        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("code") == 0:
                    user = data.get("data", {})
                    name = user.get("nickname", "")
                    if name:
                        print(f"   ✅ SUCCESS! Name: {name}, Level: {user.get('level', 1)}, Likes: {user.get('liked', 0)}")
                        return {"name": name, "level": user.get("level", 1), "likes": user.get("liked", 0), "game": "FF MAX"}

        print("   ❌ No data returned")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Method 2: FF MAX profile API
    print("\n📡 Method 2: FF MAX profile API...")
    try:
        url = f"https://ffmax.garena.com/api/profile/{uid}"

        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                name = data.get("nickname", data.get("name", ""))
                if name:
                    print(f"   ✅ SUCCESS! Name: {name}, Level: {data.get('level', 1)}, Likes: {data.get('liked', 0)}")
                    return {"name": name, "level": data.get("level", 1), "likes": data.get("liked", 0), "game": "FF MAX"}

        print("   ❌ No data returned")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Method 3: Regular FF Garena antispam API
    print("\n📡 Method 3: Regular FF Garena antispam API...")
    try:
        url = "https://ff.garena.com/api/antispam/get_user_basic_info"
        payload = json.dumps({"uid": uid, "region": "IND"}).encode('utf-8')

        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("code") == 0:
                    user = data.get("data", {})
                    name = user.get("nickname", "")
                    if name:
                        print(f"   ✅ SUCCESS! Name: {name}, Level: {user.get('level', 1)}, Likes: {user.get('liked', 0)}")
                        return {"name": name, "level": user.get("level", 1), "likes": user.get("liked", 0), "game": "FF"}

        print("   ❌ No data returned")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Method 4: Regular FF profile API
    print("\n📡 Method 4: Regular FF profile API...")
    try:
        url = f"https://ff.garena.com/api/profile/{uid}"

        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                name = data.get("nickname", data.get("name", ""))
                if name:
                    print(f"   ✅ SUCCESS! Name: {name}, Level: {data.get('level', 1)}, Likes: {data.get('liked', 0)}")
                    return {"name": name, "level": data.get("level", 1), "likes": data.get("liked", 0), "game": "FF"}

        print("   ❌ No data returned")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Method 5: Alternative APIs
    print("\n📡 Method 5: Alternative third-party APIs...")
    apis = [
        ("freefireinfo.site", f"https://freefireinfo.site/api/info/sg/{uid}"),
        ("api-freefire.vercel.app", f"https://api-freefire.vercel.app/api/profile/{uid}"),
        ("ff-api.com", f"https://ff-api.com/player/{uid}")
    ]

    for api_name, api_url in apis:
        try:
            print(f"   📡 Trying {api_name}...")
            req = urllib.request.Request(api_url, headers=headers, method='GET')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    name = data.get("nickname") or data.get("name") or data.get("accountName") or data.get("playerName") or ""
                    if name:
                        likes = data.get("likes") or data.get("liked") or 0
                        level = data.get("level") or 1
                        print(f"   ✅ SUCCESS! Name: {name}, Level: {level}, Likes: {likes}")
                        return {"name": name, "level": level, "likes": likes, "game": f"Third-party ({api_name})"}
        except Exception as e:
            print(f"   ❌ {api_name} failed: {e}")

    # All methods failed
    print("\n⚠️  All methods failed!")
    return None


if __name__ == "__main__":
    uid = "1810201201"

    result = test_all_apis(uid)

    print(f"\n{'='*70}")
    print("FINAL RESULT:")
    print(f"{'='*70}")

    if result:
        print(f"👤 In-Game Name:  {result['name']}")
        print(f"📊 Level:         {result['level']}")
        print(f"❤️  Current Likes: {result['likes']}")
        print(f"🎮 Game Type:     {result['game']}")
    else:
        print(f"❌ Could not fetch player info for UID {uid}")
        print(f"\nPossible reasons:")
        print(f"  • UID does not exist")
        print(f"  • Player has strict privacy settings")
        print(f"  • All Garena APIs are temporarily down")

    print(f"{'='*70}\n")
