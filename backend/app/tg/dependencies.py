from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from app.config import config_manager
from app.db import get_session
from app.tg.init_data_validator import validate_init_data
from app.users.models import Users
from app.users.services import get_or_create_user


async def get_current_user(
    init_data: Optional[str] = Header(None, alias="X-Init-Data"),
    tg_id: Optional[int] = Header(None, alias="X-Tg-Id"),
    session: Session = Depends(get_session)
) -> Users:
    """
    Get current user from Telegram initData or direct tg_id header.
    In development mode, allows direct tg_id for testing.
    """
    bot_token = config_manager.get_bot_token()

    if init_data:
        result = validate_init_data(init_data, bot_token)

        if not result.is_valid:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid initData: {result.error}"
            )

        if not result.user:
            raise HTTPException(
                status_code=401,
                detail="No user data in initData"
            )

        user, _ = get_or_create_user(
            session,
            tg_id=result.user.id,
            username=result.user.username,
            first_name=result.user.first_name,
            last_name=result.user.last_name
        )
        return user

    if tg_id:
        user, _ = get_or_create_user(session, tg_id=tg_id)
        return user

    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide X-Init-Data header."
    )
