"""
Telegram WebApp initData validator.

Validates the initData string from Telegram Mini App to ensure
the request is authenticated and not tampered with.
"""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qs, unquote

logger = logging.getLogger(__name__)

INIT_DATA_MAX_AGE = 86400  # 24 hours


@dataclass
class TelegramUser:
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    allows_write_to_pm: bool = False
    photo_url: Optional[str] = None


@dataclass
class InitDataValidationResult:
    is_valid: bool
    user: Optional[TelegramUser] = None
    error: Optional[str] = None
    auth_date: Optional[int] = None
    query_id: Optional[str] = None
    chat_instance: Optional[str] = None
    chat_type: Optional[str] = None
    start_param: Optional[str] = None


def validate_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int = INIT_DATA_MAX_AGE
) -> InitDataValidationResult:
    try:
        if not init_data:
            return InitDataValidationResult(
                is_valid=False,
                error="Empty initData"
            )

        parsed = parse_qs(init_data)

        received_hash = parsed.get('hash', [None])[0]
        if not received_hash:
            return InitDataValidationResult(
                is_valid=False,
                error="Missing hash in initData"
            )

        auth_date_str = parsed.get('auth_date', [None])[0]
        if not auth_date_str:
            return InitDataValidationResult(
                is_valid=False,
                error="Missing auth_date in initData"
            )

        try:
            auth_date = int(auth_date_str)
        except ValueError:
            return InitDataValidationResult(
                is_valid=False,
                error="Invalid auth_date format"
            )

        current_time = int(time.time())
        if current_time - auth_date > max_age_seconds:
            return InitDataValidationResult(
                is_valid=False,
                error=f"initData expired (age: {current_time - auth_date}s)"
            )

        data_check_parts = []
        for key in sorted(parsed.keys()):
            if key != 'hash':
                value = parsed[key][0] if parsed[key] else ''
                data_check_parts.append(f"{key}={value}")

        data_check_string = '\n'.join(data_check_parts)

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode('utf-8'),
            hashlib.sha256
        ).digest()

        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_hash, received_hash):
            logger.warning(f"Hash mismatch in initData validation")
            return InitDataValidationResult(
                is_valid=False,
                error="Invalid hash - data may be tampered"
            )

        user_json = parsed.get('user', [None])[0]
        if not user_json:
            return InitDataValidationResult(
                is_valid=False,
                error="Missing user data in initData"
            )

        try:
            user_data = json.loads(unquote(user_json))
        except json.JSONDecodeError as e:
            return InitDataValidationResult(
                is_valid=False,
                error=f"Invalid user JSON: {str(e)}"
            )

        user = TelegramUser(
            id=user_data.get('id'),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name'),
            username=user_data.get('username'),
            language_code=user_data.get('language_code'),
            is_premium=user_data.get('is_premium', False),
            allows_write_to_pm=user_data.get('allows_write_to_pm', False),
            photo_url=user_data.get('photo_url')
        )

        if not user.id:
            return InitDataValidationResult(
                is_valid=False,
                error="Missing user ID in initData"
            )

        return InitDataValidationResult(
            is_valid=True,
            user=user,
            auth_date=auth_date,
            query_id=parsed.get('query_id', [None])[0],
            chat_instance=parsed.get('chat_instance', [None])[0],
            chat_type=parsed.get('chat_type', [None])[0],
            start_param=parsed.get('start_param', [None])[0]
        )

    except Exception as e:
        logger.error(f"Error validating initData: {str(e)}", exc_info=True)
        return InitDataValidationResult(
            is_valid=False,
            error=f"Validation error: {str(e)}"
        )
