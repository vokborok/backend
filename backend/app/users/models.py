from datetime import datetime
from typing import Any, Dict, Optional

from sqlmodel import Column, Field, BigInteger, SQLModel, JSON

from app.lib.mixins import HasCreatedAt, HasSequenceID, HasUpdatedAt


class Users(SQLModel, HasSequenceID, HasCreatedAt, HasUpdatedAt, table=True):
    __tablename__: str = "users"

    tg_id: int = Field(
        sa_column=Column(BigInteger, index=True, unique=True, nullable=False)
    )

    soft_currency: int = Field(default=0)
    hard_currency: int = Field(default=0)

    experience: int = Field(default=0)
    level: int = Field(default=1)

    energy: int = Field(default=100)
    max_energy: int = Field(default=100)
    energy_last_update: Optional[datetime] = Field(default=None)
    energy_notification_sent: bool = Field(default=True)

    tutorial_step: int = Field(default=0)
    last_activity: Optional[datetime] = Field(default=None)

    settings_data: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=True), default=None
    )
    game_data: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=True), default=None
    )
