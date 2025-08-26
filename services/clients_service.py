"""Business logic for managing clients."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List, Optional

from models.client import Client
from repositories.clients_repository import ClientsRepository

ALLOWED_SEX = {"Homme", "Femme", "Autre"}


class ClientsService:
    """Service layer that validates data and interacts with repository."""

    def __init__(self, repo: ClientsRepository) -> None:
        self.repo = repo

    # ------------------------------------------------------------------
    def create(self, data: Dict[str, object]) -> Client:
        """Create a new client after validating input."""
        self._validate(data)
        if self.repo.get_by_identity(data["first_name"], data["last_name"], data["birthdate"]):
            raise ValueError("A client with this name and birthdate already exists")
        client = Client(
            id=str(uuid.uuid4()),
            first_name=data["first_name"],
            last_name=data["last_name"],
            sex=data["sex"],
            birthdate=data["birthdate"],
            height_cm=data["height_cm"],
            weight_kg=data["weight_kg"],
            objective=data.get("objective"),
            injuries=data.get("injuries"),
            email=data.get("email"),
            phone=data.get("phone"),
        )
        self.repo.add(client)
        return client

    def get(self, client_id: str) -> Optional[Client]:
        return self.repo.get(client_id)

    def update(self, client_id: str, data: Dict[str, object]) -> Client:
        existing = self.repo.get(client_id)
        if not existing:
            raise ValueError("Client not found")
        merged = existing.__dict__ | data
        self._validate(merged)
        if (
            merged["first_name"],
            merged["last_name"],
            merged["birthdate"],
        ) != (existing.first_name, existing.last_name, existing.birthdate):
            dup = self.repo.get_by_identity(
                merged["first_name"], merged["last_name"], merged["birthdate"]
            )
            if dup and dup.id != client_id:
                raise ValueError("A client with this name and birthdate already exists")
        updated = Client(
            id=existing.id,
            first_name=merged["first_name"],
            last_name=merged["last_name"],
            sex=merged["sex"],
            birthdate=merged["birthdate"],
            height_cm=merged["height_cm"],
            weight_kg=merged["weight_kg"],
            objective=merged.get("objective"),
            injuries=merged.get("injuries"),
            email=merged.get("email"),
            phone=merged.get("phone"),
            created_at=existing.created_at,
        )
        self.repo.update(updated)
        return updated

    def list_all(self) -> List[Client]:
        return self.repo.list_all()

    def delete(self, client_id: str) -> None:
        client = self.repo.get(client_id)
        if not client:
            raise ValueError("Client not found")
        anonymized = Client(
            id=client.id,
            first_name="Anonyme",
            last_name="Anonyme",
            sex=client.sex,
            birthdate=client.birthdate,
            height_cm=client.height_cm,
            weight_kg=client.weight_kg,
            objective=client.objective,
            injuries=client.injuries,
            email=None,
            phone=None,
            created_at=client.created_at,
        )
        self.repo.update(anonymized)
        self.repo.delete(client_id)

    # ------------------------------------------------------------------
    def _validate(self, data: Dict[str, object]) -> None:
        for field in ["first_name", "last_name", "sex", "birthdate", "height_cm", "weight_kg"]:
            value = data.get(field)
            if value is None or value == "":
                raise ValueError(f"{field} is required")
        if data["sex"] not in ALLOWED_SEX:
            raise ValueError("Invalid sex")
        birthdate = data["birthdate"]
        if not isinstance(birthdate, date):
            raise ValueError("birthdate must be a date")
        if birthdate > date.today():
            raise ValueError("birthdate cannot be in the future")
        if float(data["height_cm"]) <= 0:
            raise ValueError("height_cm must be positive")
        if float(data["weight_kg"]) <= 0:
            raise ValueError("weight_kg must be positive")


__all__ = ["ClientsService"]
