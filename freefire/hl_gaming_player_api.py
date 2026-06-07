"""
HL Gaming Official Player Info API
100% working method to get real player names, levels, likes
"""

import os
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)

# HL Gaming Official API
API_BASE = "https://proapis.hlgamingofficial.com/main/games/freefire"
USER_UID = os.getenv("HL_GAMING_USERUID", "")
API_KEY = os.getenv("HL_GAMING_API_KEY", "")


def get_player_info_hl_gaming(uid: str, region: str = "ind") -> dict:
    """
    Get player info using HL Gaming Official API

    Args:
        uid: Player UID
        region: Server region (ind, br, sg, us, etc.)

    Returns:
        Dict with player information or error
    """

    if not USER_UID or not API_KEY:
        logger.error("HL Gaming API credentials not configured!")
        return {
            'success': False,
            'error': 'API_NOT_CONFIGURED',
            'message': 'HL Gaming API credentials missing. Add HL_GAMING_USERUID and HL_GAMING_API_KEY to environment variables.'
        }

    try:
        params = {
            'sectionName': 'AllData',
            'PlayerUid': uid,
            'region': region,
            'useruid': USER_UID,
            'api': API_KEY
        }

        url = f"{API_BASE}/account/api"
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        req = urllib.request.Request(full_url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                # Extract account info
                account_info = data.get('AccountInfo', {})
                guild_info = data.get('GuildInfo', {})

                nickname = account_info.get('nickname', account_info.get('name', ''))
                level = account_info.get('level', account_info.get('accountLevel', 1))
                likes = account_info.get('likes', account_info.get('liked', 0))
                rank = account_info.get('rank', account_info.get('rankName', ''))
                guild_name = guild_info.get('guildName', guild_info.get('clanName', ''))

                logger.info(f"✅ HL Gaming API: Got player info for {uid}: {nickname}")

                return {
                    'success': True,
                    'name': nickname,
                    'level': level,
                    'likes': likes,
                    'rank': rank,
                    'guild': guild_name,
                    'uid': uid,
                    'region': region,
                    'method': 'HL Gaming Official API'
                }

        logger.error(f"HL Gaming API returned status {response.status}")
        return {
            'success': False,
            'error': f'HTTP_{response.status}',
            'message': f'API returned status code {response.status}'
        }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        logger.error(f"HL Gaming API HTTP Error {e.code}: {e.reason} - {error_body}")

        if e.code == 403:
            return {
                'success': False,
                'error': 'INVALID_CREDENTIALS',
                'message': 'Invalid HL Gaming API credentials. Check your useruid and api key.'
            }
        elif e.code == 404:
            return {
                'success': False,
                'error': 'UID_NOT_FOUND',
                'message': f'Player UID {uid} not found in region {region}. Check UID and region.'
            }
        else:
            return {
                'success': False,
                'error': f'HTTP_{e.code}',
                'message': f'{e.reason}'
            }

    except Exception as e:
        logger.error(f"HL Gaming API Error: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'UNKNOWN_ERROR',
            'message': str(e)
        }
