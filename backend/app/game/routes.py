"""
Game routes - example game endpoints.
Extend this with your game-specific logic.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.energy.config import DEFAULT_ENERGY_COST
from app.energy.services import spend_energy, update_user_energy
from app.tg.dependencies import get_current_user
from app.users.models import Users
from app.users.services import get_user_data_response

game_router = APIRouter()


class GameActionRequest(BaseModel):
    action: str
    data: dict = {}


class GameActionResponse(BaseModel):
    success: bool
    message: str = ""
    user: dict = {}
    result: dict = {}


@game_router.post("/game/action")
async def game_action(
    request: GameActionRequest,
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
) -> GameActionResponse:
    """
    Generic game action endpoint.
    Override or extend this for your specific game logic.
    """
    user = update_user_energy(session, user)

    if request.action == "start_game":
        success, message = spend_energy(session, user, DEFAULT_ENERGY_COST)
        if not success:
            return GameActionResponse(
                success=False,
                message=message,
                user=get_user_data_response(user)
            )

        return GameActionResponse(
            success=True,
            message="Game started",
            user=get_user_data_response(user),
            result={"game_id": "example_game_123"}
        )

    elif request.action == "end_game":
        score = request.data.get("score", 0)
        user.experience += score // 10
        session.commit()

        return GameActionResponse(
            success=True,
            message=f"Game ended. Score: {score}",
            user=get_user_data_response(user),
            result={"score": score, "exp_gained": score // 10}
        )

    return GameActionResponse(
        success=False,
        message=f"Unknown action: {request.action}",
        user=get_user_data_response(user)
    )


@game_router.get("/game/state")
async def get_game_state(
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
):
    """
    Get current game state for user.
    """
    user = update_user_energy(session, user)

    return {
        "success": True,
        "user": get_user_data_response(user),
        "game_data": user.game_data or {}
    }


@game_router.post("/game/save")
async def save_game_state(
    game_data: dict,
    session: Session = Depends(get_session),
    user: Users = Depends(get_current_user)
):
    """
    Save game state for user.
    """
    user.game_data = game_data
    session.commit()

    return {
        "success": True,
        "message": "Game state saved"
    }
