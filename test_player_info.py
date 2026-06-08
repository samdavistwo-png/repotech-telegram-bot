#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

USER_UID = "txnuOflAvIQxwFsfZ8GkTygDYcg2"
API_KEY = "jO6UCe7EARqYsxXkJSkwCweJ0T2ii3"

print("=" * 60)
print("TESTING PLAYER INFO API")
print("=" * 60)

test_uid = "1810201201"

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

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }

    req = urllib.request.Request(full_url, headers=headers, method='GET')

    with urllib.request.urlopen(req, timeout=15) as response:
        print(f"Status: {response.status}")
        data = json.loads(response.read().decode('utf-8'))

        account_info = data.get('AccountInfo', {})
        nickname = account_info.get('nickname', account_info.get('name', ''))
        level = account_info.get('level', 1)
        likes = account_info.get('likes', 0)

        print(f"Player: {nickname}")
        print(f"Level: {level}")
        print(f"Likes: {likes:,}")
        print("PLAYER INFO API WORKS!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
