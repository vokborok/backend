from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.users.models import Users


def get_user_by_tg_id(session: Session, tg_id: int) -> Optional[Users]:
    statement = select(Users).where(Users.tg_id == tg_id)
    return session.exec(statement).first()


def create_user(session: Session, tg_id: int) -> Users:
    user = Users(
        tg_id=tg_id,
        energy_last_update=datetime.utcnow(),
        last_activity=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_or_create_user(session: Session, tg_id: int) -> tuple[Users, bool]:
    """Получить пользователя или создать нового.
    
    Returns:
        tuple[Users, bool]: (user, created) - пользователь и флаг создания
    """
    user = get_user_by_tg_id(session, tg_id)
    if user:
        user.last_activity = datetime.utcnow()
        session.commit()
        return user, False

    user = create_user(session, tg_id)
    return user, True


def update_user_currency(
    session: Session,
    user: Users,
    soft_delta: int = 0,
    hard_delta: int = 0
) -> Users:
    if soft_delta:
        user.soft_currency = max(0, user.soft_currency + soft_delta)
    if hard_delta:
        user.hard_currency = max(0, user.hard_currency + hard_delta)
    session.commit()
    session.refresh(user)
    return user


def add_experience(session: Session, user: Users, exp: int) -> Users:
    user.experience += exp
    session.commit()
    session.refresh(user)
    return user


def get_user_data_response(user: Users) -> dict:
    return {
        "tg_id": user.tg_id,
        "soft_currency": user.soft_currency,
        "hard_currency": user.hard_currency,
        "experience": user.experience,
        "level": user.level,
        "energy": user.energy,
        "max_energy": user.max_energy,
        "tutorial_step": user.tutorial_step,
        "settings_data": user.settings_data,
        "game_data": user.game_data
    }
