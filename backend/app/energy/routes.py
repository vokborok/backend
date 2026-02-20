from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.energy.config import DEFAULT_ENERGY_COST
from app.energy.services import (
    get_time_to_full_energy,
    spend_energy,
    update_user_energy,
)
from app.tg.dependencies import get_current_user
from app.users.models import Users

energy_router = APIRouter()


class SpendEnergyRequest(BaseModel):
    amount: int = DEFAULT_ENERGY_COST


@energy_router.get("/energy")
async def get_energy(
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
):
    user = update_user_energy(session, user)
    return {
        "success": True,
        "energy": user.energy,
        "max_energy": user.max_energy,
        "time_to_full": get_time_to_full_energy(user)
    }


@energy_router.post("/energy/spend")
async def spend_user_energy(
    request: SpendEnergyRequest,
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
):
    success, message = spend_energy(session, user, request.amount)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "energy": user.energy,
        "max_energy": user.max_energy,
        "time_to_full": get_time_to_full_energy(user)
    }
