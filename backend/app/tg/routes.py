import logging
import os

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlmodel import Session

from app.config import config_manager
from app.db import get_session
from app.tg.dependencies import get_current_user
from app.tg.init_data_validator import validate_init_data
from app.users.models import Users
from app.users.services import get_or_create_user, get_user_data_response

logger = logging.getLogger(__name__)

telegram_router = APIRouter()


class LoginRequest(BaseModel):
    init_data: str


@telegram_router.post("/login")
async def telegram_login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login endpoint for Telegram Mini App.
    Validates initData and creates/updates user.
    """
    bot_token = config_manager.get_bot_token()
    result = validate_init_data(request.init_data, bot_token)

    if not result.is_valid:
        return {
            "success": False,
            "error": result.error
        }

    if not result.user:
        return {
            "success": False,
            "error": "No user data in initData"
        }

    user, is_new = get_or_create_user(
        session,
        tg_id=result.user.id,
        username=result.user.username,
        first_name=result.user.first_name,
        last_name=result.user.last_name
    )

    return {
        "success": True,
        "is_new_user": is_new,
        "user": get_user_data_response(user)
    }


@telegram_router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Webhook endpoint for Telegram Bot updates.
    Handle bot commands, payments, etc.
    """
    try:
        data = await request.json()
        logger.debug(f"Webhook received: {data}")

        if "message" in data:
            message = data["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")

            if text.startswith("/start"):
                logger.info(f"Start command from chat {chat_id}")

            elif text.startswith("/help"):
                logger.info(f"Help command from chat {chat_id}")

        if "pre_checkout_query" in data:
            logger.info(f"Pre-checkout query: {data['pre_checkout_query']}")

        if "successful_payment" in data.get("message", {}):
            payment = data["message"]["successful_payment"]
            logger.info(f"Successful payment: {payment}")

        return {"ok": True}

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
