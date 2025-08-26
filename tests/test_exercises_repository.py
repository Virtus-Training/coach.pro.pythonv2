import sqlite3
import uuid
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.exercise import Exercise
from repositories.exercises_repository import ExercisesRepository


def setup_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    with open("db/migrations/0002_create_exercises_table.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    return conn


def test_create_and_get_by_id():
    conn = setup_db()
    repo = ExercisesRepository(conn)
    ex = Exercise(id=str(uuid.uuid4()), name="Pompe", slug="pompe", primary_muscle="PECTORAUX")
    repo.create(ex)
    fetched = repo.get_by_id(ex.id)
    assert fetched is not None
    assert fetched.name == "Pompe"
    assert repo.get_by_id("missing") is None


def test_list_and_update_and_soft_delete():
    conn = setup_db()
    repo = ExercisesRepository(conn)
    ex1 = Exercise(id="1", name="Squat", slug="squat", primary_muscle="QUADRICEPS", equipment="BAR")
    ex2 = Exercise(
        id="2",
        name="Traction",
        slug="traction",
        primary_muscle="DORSAUX",
        equipment="BW",
    )
    repo.create(ex1)
    repo.create(ex2)
    # list filter
    res = repo.list_all(name="Squat", primary_muscle="QUADRICEPS", equipment="BAR")
    assert len(res) == 1 and res[0].id == "1"
    assert repo.get_by_name("Traction").id == "2"
    # update
    ex1.name = "Front Squat"
    ex1.slug = "front-squat"
    repo.update(ex1)
    assert repo.get_by_id("1").name == "Front Squat"
    # soft delete
    repo.soft_delete("2")
    assert repo.get_by_id("2").is_active == 0


def test_is_used_in_session():
    conn = setup_db()
    repo = ExercisesRepository(conn)
    ex_id = "ex-1"
    ex = Exercise(id=ex_id, name="Crunch", slug="crunch", primary_muscle="ABDOMINAUX")
    repo.create(ex)
    conn.execute(
        "INSERT INTO session_exercises (session_id, exercise_id, sets, repetitions) VALUES (1, ?, 3, 10)",
        (ex_id,),
    )
    assert repo.is_used_in_session(ex_id) is True
    assert repo.is_used_in_session("not-used") is False
