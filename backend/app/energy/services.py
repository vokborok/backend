from datetime import datetime
from typing import Tuple

from sqlmodel import Session

from app.energy.config import ENERGY_REGEN_PER_MINUTE, MAX_ENERGY
from app.users.models import Users


def calculate_current_energy(user: Users) -> Tuple[int, datetime]:
    """
    Calculate current energy based on time passed since last update.
    Returns tuple of (current_energy, new_last_update_time).
    """
    now = datetime.utcnow()

    if user.energy_last_update is None:
        return user.energy, now

    time_diff = now - user.energy_last_update
    minutes_passed = time_diff.total_seconds() / 60

    if minutes_passed <= 0:
        return user.energy, user.energy_last_update

    energy_gained = int(minutes_passed * ENERGY_REGEN_PER_MINUTE)
    max_energy = user.max_energy or MAX_ENERGY

    if energy_gained == 0:
        return user.energy, user.energy_last_update

    new_energy = min(user.energy + energy_gained, max_energy)

    return new_energy, now


def update_user_energy(session: Session, user: Users) -> Users:
    """
    Update user's energy based on time passed.
    """
    new_energy, new_time = calculate_current_energy(user)

    if new_energy != user.energy:
        user.energy = new_energy
        user.energy_last_update = new_time
        session.commit()
        session.refresh(user)

    return user


def spend_energy(session: Session, user: Users, amount: int) -> Tuple[bool, str]:
    """
    Spend energy. Returns (success, message).
    """
    user = update_user_energy(session, user)

    if user.energy < amount:
        return False, f"Not enough energy. Have {user.energy}, need {amount}"

    user.energy -= amount
    user.energy_last_update = datetime.utcnow()
    user.energy_notification_sent = False
    session.commit()
    session.refresh(user)

    return True, f"Spent {amount} energy. Remaining: {user.energy}"


def restore_energy(session: Session, user: Users, amount: int) -> Users:
    """
    Restore energy (e.g., from purchase or reward).
    """
    max_energy = user.max_energy or MAX_ENERGY
    user.energy = min(user.energy + amount, max_energy)
    user.energy_last_update = datetime.utcnow()
    session.commit()
    session.refresh(user)
    return user


def set_full_energy(session: Session, user: Users) -> Users:
    """
    Set energy to max.
    """
    max_energy = user.max_energy or MAX_ENERGY
    user.energy = max_energy
    user.energy_last_update = datetime.utcnow()
    session.commit()
    session.refresh(user)
    return user


def get_time_to_full_energy(user: Users) -> int:
    """
    Get time in seconds until energy is fully restored.
    """
    max_energy = user.max_energy or MAX_ENERGY
    if user.energy >= max_energy:
        return 0

    energy_needed = max_energy - user.energy
    minutes_needed = energy_needed / ENERGY_REGEN_PER_MINUTE
    return int(minutes_needed * 60)
