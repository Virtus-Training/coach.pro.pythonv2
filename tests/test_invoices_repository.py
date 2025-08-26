import sqlite3
import uuid
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.invoice import Invoice
from repositories.invoices_repository import InvoicesRepository


def setup_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON;")
    for mig in [
        "db/migrations/0003_create_clients_table.sql",
        "db/migrations/0004_create_invoices_table.sql",
    ]:
        with open(mig, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    return conn


def test_crud_and_on_delete_set_null():
    conn = setup_db()
    repo = InvoicesRepository(conn)
    client_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO clients (
            id, first_name, last_name, sex, birthdate,
            height_cm, weight_kg, objective, injuries, email, phone, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,0)
        """,
        (
            client_id,
            "John",
            "Doe",
            "Homme",
            "1990-01-01",
            180.0,
            80.0,
            None,
            None,
            None,
            None,
        ),
    )
    inv = Invoice(
        id=str(uuid.uuid4()),
        client_id=client_id,
        number="2024-001",
        label="Coaching",
        amount_cents=10000,
        status="Non payée",
        issued_on=date(2024, 1, 1),
        template="classic",
    )
    repo.add(inv)
    fetched = repo.get(inv.id)
    assert fetched and fetched.number == "2024-001"
    assert len(repo.list_all()) == 1
    inv.label = "Updated"
    repo.update(inv)
    assert repo.get(inv.id).label == "Updated"
    conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    assert repo.get(inv.id).client_id is None
    repo.delete(inv.id)
    assert repo.get(inv.id) is None
