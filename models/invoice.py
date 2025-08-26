"""Data model for invoice entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Invoice:
    """Dataclass representing an invoice record."""

    id: str
    client_id: Optional[str]
    number: str
    label: Optional[str]
    amount_cents: int
    status: str
    issued_on: date
    paid_on: Optional[date] = None
    pdf_path: Optional[str] = None
    template: str = "classic"


__all__ = ["Invoice"]
