import sqlite3
import uuid
from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.client import Client
from repositories.clients_repository import ClientsRepository


def setup_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON;")
    with open("db/migrations/0003_create_clients_table.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


def test_crud_and_on_delete_set_null():
    conn = setup_db()
    repo = ClientsRepository(conn)
    c1 = Client(
        id=str(uuid.uuid4()),
        first_name="John",
        last_name="Doe",
        sex="Homme",
        birthdate=date(1990, 1, 1),
        email="john@example.com",
        phone="123",
    )
    c2 = Client(
        id=str(uuid.uuid4()),
        first_name="Jane",
        last_name="Doe",
        sex="Femme",
        birthdate=date(1992, 2, 2),
        email="jane@example.com",
        phone="456",
    )
    repo.add(c1)
    repo.add(c2)
    assert repo.get(c1.id).first_name == "John"
    assert len(repo.list_all()) == 2
    c1.first_name = "Johnny"
    repo.update(c1)
    assert repo.get(c1.id).first_name == "Johnny"
    conn.execute(
        "INSERT INTO sessions (client_id, session_date) VALUES (?, ?)",
        (c1.id, "2024-01-01"),
    )
    repo.delete(c1.id)
    assert repo.get(c1.id) is None
    assert conn.execute("SELECT client_id FROM sessions").fetchone()[0] is None
    dup = Client(
        id=str(uuid.uuid4()),
        first_name="Jane",
        last_name="Doe",
        sex="Femme",
        birthdate=date(1992, 2, 2),
        email="other@example.com",
        phone="789",
    )
    try:
        repo.add(dup)
    except sqlite3.IntegrityError:
        pass
    else:
        assert False, "unique constraint failed"
