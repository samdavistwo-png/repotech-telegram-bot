"""
HL Gaming Official Likes Sender API
100% working method to send likes instantly
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


def send_likes_hl_gaming(target_uid: str, amount: int = 100, region: str = "ind") -> dict:
    """
    Send likes using HL Gaming Official API

    Args:
        target_uid: Target player UID
        amount: Number of likes to send (default: 100)
        region: Server region (ind, br, sg, us, etc.)

    Returns:
        Dict with result information
    """

    if not USER_UID or not API_KEY:
        logger.error("HL Gaming API credentials not configured!")
        return {
            'success': False,
            'error': 'API_NOT_CONFIGURED',
            'message': 'HL Gaming API credentials missing'
        }

    try:
        params = {
            'targetUid': target_uid,
            'amount': str(amount),
            'region': region,
            'useruid': USER_UID,
            'api': API_KEY
        }

        url = f"{API_BASE}/likes/api"
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        req = urllib.request.Request(full_url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                logger.info(f"✅ HL Gaming API: Sent {amount} likes to {target_uid}")

                return {
                    'success': True,
                    'likes_sent': amount,
                    'target_uid': target_uid,
                    'message': data.get('message', 'Likes sent successfully'),
                    'details': data
                }

        logger.error(f"HL Gaming Likes API returned status {response.status}")
        return {
            'success': False,
            'error': f'HTTP_{response.status}',
            'message': f'API returned status code {response.status}'
        }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        logger.error(f"HL Gaming Likes API HTTP Error {e.code}: {e.reason} - {error_body}")

        if e.code == 403:
            return {
                'success': False,
                'error': 'INVALID_CREDENTIALS',
                'message': 'Invalid HL Gaming API credentials'
            }
        elif e.code == 429:
            return {
                'success': False,
                'error': 'RATE_LIMIT',
                'message': 'API rate limit exceeded. Please try again later.'
            }
        else:
            return {
                'success': False,
                'error': f'HTTP_{e.code}',
                'message': f'{e.reason}'
            }

    except Exception as e:
        logger.error(f"HL Gaming Likes API Error: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'UNKNOWN_ERROR',
            'message': str(e)
        }
