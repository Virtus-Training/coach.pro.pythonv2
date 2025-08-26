import sqlite3
import time
import uuid
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.exercise import Exercise
from repositories.exercises_repository import ExercisesRepository


def setup_db(count: int = 0) -> ExercisesRepository:
    conn = sqlite3.connect(":memory:")
    with open("db/migrations/0002_create_exercises_table.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    repo = ExercisesRepository(conn)
    for i in range(count):
        ex = Exercise(
            id=str(uuid.uuid4()),
            name=f"Exercice {i}",
            slug=f"ex{i}",
            primary_muscle="PECTORAUX",
            equipment="BAR",
            pattern="PH",
            difficulty=3,
        )
        repo.create(ex)
    return repo


def test_search_filters():
    repo = setup_db(5)
    res = repo.search(query="Exercice 1", primary_muscles=["PECTORAUX"], equipment=["BAR"], patterns=["PH"], difficulty=(1,5))
    assert res and res[0].name == "Exercice 1"
    res = repo.search(query="Inexistant")
    assert res == []


def test_search_performance():
    repo = setup_db(1000)
    start = time.perf_counter()
    repo.search(query="Exercice", primary_muscles=["PECTORAUX"], equipment=["BAR"], difficulty=(1,5))
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 150
