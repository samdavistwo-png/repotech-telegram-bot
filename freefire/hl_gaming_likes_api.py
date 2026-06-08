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
            'ff_uid': target_uid,  # Fixed: API expects 'ff_uid' not 'targetUid'
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

        # Try to parse error response for better error messages
        try:
            error_data = json.loads(error_body)
            error_message = error_data.get('message', e.reason)
            error_code = error_data.get('error_code', 'UNKNOWN')

            # Check for plan limitation errors
            if error_code == 'AUTH_FAILED' or 'not available for this plan' in error_message.lower():
                return {
                    'success': False,
                    'error': 'API_PLAN_LIMITATION',
                    'message': 'HL Gaming Likes API not available in your subscription plan. Please upgrade at https://www.hlgamingofficial.com/p/api.html'
                }
        except:
            pass

        if e.code == 403:
            return {
                'success': False,
                'error': 'FORBIDDEN',
                'message': 'Access denied. Check your HL Gaming API subscription plan or credentials at https://www.hlgamingofficial.com/p/api.html'
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
