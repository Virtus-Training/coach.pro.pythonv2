"""Repository handling database operations for invoices."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from models.invoice import Invoice


class InvoicesRepository:
    """Encapsulates CRUD operations for invoices table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # ------------------------------------------------------------------
    def _row_to_invoice(self, row: sqlite3.Row | None) -> Optional[Invoice]:
        if row is None:
            return None
        issued = date.fromisoformat(row[6])
        paid = date.fromisoformat(row[7]) if row[7] else None
        return Invoice(
            id=row[0],
            client_id=row[1],
            number=row[2],
            label=row[3],
            amount_cents=row[4],
            status=row[5],
            issued_on=issued,
            paid_on=paid,
            pdf_path=row[8],
            template=row[9],
        )

    # ------------------------------------------------------------------
    def add(self, invoice: Invoice) -> None:
        """Insert a new invoice into the database."""
        data = (
            invoice.id,
            invoice.client_id,
            invoice.number,
            invoice.label,
            invoice.amount_cents,
            invoice.status,
            invoice.issued_on.isoformat(),
            invoice.paid_on.isoformat() if invoice.paid_on else None,
            invoice.pdf_path,
            invoice.template,
        )
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO invoices (
                    id, client_id, number, label, amount_cents, status,
                    issued_on, paid_on, pdf_path, template
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                data,
            )

    def get(self, invoice_id: str) -> Optional[Invoice]:
        row = self.conn.execute(
            "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
        ).fetchone()
        return self._row_to_invoice(row)

    def list_all(self) -> List[Invoice]:
        rows = self.conn.execute("SELECT * FROM invoices").fetchall()
        return [self._row_to_invoice(r) for r in rows if r]

    def update(self, invoice: Invoice) -> None:
        data = (
            invoice.client_id,
            invoice.number,
            invoice.label,
            invoice.amount_cents,
            invoice.status,
            invoice.issued_on.isoformat(),
            invoice.paid_on.isoformat() if invoice.paid_on else None,
            invoice.pdf_path,
            invoice.template,
            invoice.id,
        )
        with self.conn:
            self.conn.execute(
                """
                UPDATE invoices SET
                    client_id=?, number=?, label=?, amount_cents=?, status=?,
                    issued_on=?, paid_on=?, pdf_path=?, template=?
                WHERE id=?
                """,
                data,
            )

    def delete(self, invoice_id: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))

    def get_last_number(self, year: int) -> Optional[str]:
        row = self.conn.execute(
            "SELECT number FROM invoices WHERE number LIKE ? ORDER BY number DESC LIMIT 1",
            (f"{year}-%",),
        ).fetchone()
        return row[0] if row else None


__all__ = ["InvoicesRepository"]
