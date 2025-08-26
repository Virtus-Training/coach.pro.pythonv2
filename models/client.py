"""Data model for client entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Client:
    """Dataclass representing a client record."""

    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None
    birthdate: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    objective: Optional[str] = None
    injuries: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: int = 0


__all__ = ["Client"]
