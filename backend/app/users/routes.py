from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import logging

from app.db import get_session
from app.tg.dependencies import get_current_user
from app.users.models import Users
from app.users.services import get_user_data_response, update_user_currency, get_or_create_user
from app.energy.services import update_user_energy

logger = logging.getLogger(__name__)

users_router = APIRouter()


@users_router.get("/login")
async def login(
    tg_id: int,
    session: Session = Depends(get_session)
):
    """
    Логин пользователя. Создаёт нового пользователя если не существует.
    Обновляет энергию на основе времени.
    
    Args:
        tg_id: Telegram ID пользователя
    
    Returns:
        user_data: данные пользователя
        game_data: игровые данные (инвентарь, прогресс и т.д.)
    """
    logger.info(f"Login request for tg_id: {tg_id}")
    
    # Получаем или создаём пользователя
    user, created = get_or_create_user(session, tg_id)
    
    if created:
        logger.info(f"Created new user for tg_id: {tg_id}")
    
    # Обновляем энергию на основе времени
    user = update_user_energy(session, user)
    
    logger.info(f"Login successful for tg_id: {tg_id}, energy: {user.energy}")
    
    return {
        "success": True,
        "created": created,
        "user_data": get_user_data_response(user),
        "game_data": user.game_data
    }


@users_router.get("/user")
async def get_user(
    user: Users = Depends(get_current_user)
):
    return {
        "success": True,
        "user": get_user_data_response(user)
    }


@users_router.post("/user/settings")
async def update_settings(
    settings: dict,
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
):
    user.settings_data = settings
    session.commit()
    return {
        "success": True,
        "settings": user.settings_data
    }


@users_router.post("/user/tutorial")
async def update_tutorial(
    step: int,
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
):
    user.tutorial_step = step
    session.commit()
    return {
        "success": True,
        "tutorial_step": user.tutorial_step
    }
