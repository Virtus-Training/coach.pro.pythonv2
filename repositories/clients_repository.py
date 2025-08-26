"""Repository handling database operations for clients."""
from __future__ import annotations

import sqlite3
import time
from datetime import date
from typing import List, Optional

from models.client import Client


class ClientsRepository:
    """Encapsulates CRUD operations for clients table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # ------------------------------------------------------------------
    def _row_to_client(self, row: sqlite3.Row | None) -> Optional[Client]:
        if row is None:
            return None
        birth = date.fromisoformat(row[4])
        return Client(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            sex=row[3],
            birthdate=birth,
            height_cm=row[5],
            weight_kg=row[6],
            objective=row[7],
            injuries=row[8],
            email=row[9],
            phone=row[10],
            created_at=row[11],
        )

    # ------------------------------------------------------------------
    def add(self, client: Client) -> None:
        """Insert a new client into the database."""
        now = int(time.time())
        data = (
            client.id,
            client.first_name,
            client.last_name,
            client.sex,
            client.birthdate.isoformat(),
            client.height_cm,
            client.weight_kg,
            client.objective,
            client.injuries,
            client.email,
            client.phone,
            now,
        )
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO clients (
                    id, first_name, last_name, sex, birthdate, height_cm,
                    weight_kg, objective, injuries, email, phone, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                data,
            )

    def get(self, client_id: str) -> Optional[Client]:
        row = self.conn.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
        return self._row_to_client(row)

    def get_by_identity(
        self, first_name: str, last_name: str, birthdate: date
    ) -> Optional[Client]:
        row = self.conn.execute(
            """
            SELECT * FROM clients
            WHERE first_name = ? AND last_name = ? AND birthdate = ?
            """,
            (first_name, last_name, birthdate.isoformat()),
        ).fetchone()
        return self._row_to_client(row)

    def list_all(self) -> List[Client]:
        rows = self.conn.execute("SELECT * FROM clients").fetchall()
        return [self._row_to_client(r) for r in rows if r]

    def update(self, client: Client) -> None:
        data = (
            client.first_name,
            client.last_name,
            client.sex,
            client.birthdate.isoformat(),
            client.height_cm,
            client.weight_kg,
            client.objective,
            client.injuries,
            client.email,
            client.phone,
            client.id,
        )
        with self.conn:
            self.conn.execute(
                """
                UPDATE clients SET
                    first_name=?, last_name=?, sex=?, birthdate=?, height_cm=?,
                    weight_kg=?, objective=?, injuries=?, email=?, phone=?
                WHERE id=?
                """,
                data,
            )

    def delete(self, client_id: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))


__all__ = ["ClientsRepository"]
