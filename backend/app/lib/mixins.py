from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlmodel import Field, Column, Integer, DateTime


class HasSequenceID:
    """Mixin that provides an auto-incrementing Integer ID field."""
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )


class HasCreatedAt:
    """Mixin that provides a created_at timestamp field."""
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now())
    )


class HasUpdatedAt:
    """Mixin that provides an updated_at timestamp field with auto-update."""
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )
