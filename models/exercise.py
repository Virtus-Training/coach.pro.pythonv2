"""Data model for exercise entity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Exercise:
    """Dataclass representing an exercise record."""

    id: str
    name: str
    slug: str
    primary_muscle: str
    secondary_muscles: List[str] = field(default_factory=list)
    equipment: Optional[str] = None
    pattern: Optional[str] = None
    difficulty: Optional[int] = None
    tempo: Optional[str] = None
    rep_range: Optional[str] = None
    rpe_default: Optional[float] = None
    rest_s_default: Optional[int] = None
    cues: Optional[str] = None
    image_path: Optional[str] = None
    is_active: int = 1
    created_at: int = 0
    updated_at: int = 0


__all__ = ["Exercise"]
