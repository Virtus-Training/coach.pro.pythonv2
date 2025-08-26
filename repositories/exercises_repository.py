"""Repository handling database operations for exercises."""
from __future__ import annotations

import json
import sqlite3
import time
import unicodedata
from typing import Any, List, Optional

from models.exercise import Exercise
from config.enums import (
    PRIMARY_MUSCLE_LABELS,
    PRIMARY_MUSCLE_CODES,
    EQUIPMENT_LABELS,
    EQUIPMENT_CODES,
    PATTERN_LABELS,
    PATTERN_CODES,
)


class ExercisesRepository:
    """Encapsulates CRUD operations for exercises table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.create_function("normalize", 1, self._normalize)

    # --- helpers -------------------------------------------------
    def _row_to_exercise(self, row: sqlite3.Row | None) -> Optional[Exercise]:
        if row is None:
            return None
        secondary = [
            PRIMARY_MUSCLE_CODES.get(m, m)
            for m in (json.loads(row[4]) if row[4] else [])
        ]
        return Exercise(
            id=row[0],
            name=row[1],
            slug=row[2],
            primary_muscle=PRIMARY_MUSCLE_CODES.get(row[3], row[3]),
            secondary_muscles=secondary,
            equipment=EQUIPMENT_CODES.get(row[5], row[5]) if row[5] else None,
            pattern=PATTERN_CODES.get(row[6], row[6]) if row[6] else None,
            difficulty=row[7],
            tempo=row[8],
            rep_range=row[9],
            rpe_default=row[10],
            rest_s_default=row[11],
            cues=row[12],
            image_path=row[13],
            is_active=row[14],
            created_at=row[15],
            updated_at=row[16],
        )

    # --- CRUD methods -------------------------------------------
    def create(self, exercise: Exercise) -> None:
        now = int(time.time())
        data = (
            exercise.id,
            exercise.name,
            exercise.slug,
            PRIMARY_MUSCLE_LABELS.get(exercise.primary_muscle),
            json.dumps([
                PRIMARY_MUSCLE_LABELS.get(m) for m in exercise.secondary_muscles
            ])
            if exercise.secondary_muscles
            else None,
            EQUIPMENT_LABELS.get(exercise.equipment) if exercise.equipment else None,
            PATTERN_LABELS.get(exercise.pattern) if exercise.pattern else None,
            exercise.difficulty,
            exercise.tempo,
            exercise.rep_range,
            exercise.rpe_default,
            exercise.rest_s_default,
            exercise.cues,
            exercise.image_path,
            exercise.is_active,
            now,
            now,
        )
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO exercises (
                    id, name, slug, primary_muscle, secondary_muscles, equipment,
                    pattern, difficulty, tempo, rep_range, rpe_default, rest_s_default,
                    cues, image_path, is_active, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                data,
            )

    def get_by_id(self, exercise_id: str) -> Optional[Exercise]:
        row = self.conn.execute(
            "SELECT * FROM exercises WHERE id = ?", (exercise_id,)
        ).fetchone()
        return self._row_to_exercise(row)

    def get_by_name(self, name: str) -> Optional[Exercise]:
        row = self.conn.execute(
            "SELECT * FROM exercises WHERE name = ?", (name,)
        ).fetchone()
        return self._row_to_exercise(row)

    def list_all(
        self,
        *,
        name: str | None = None,
        primary_muscle: str | None = None,
        equipment: str | None = None,
    ) -> List[Exercise]:
        query = "SELECT * FROM exercises WHERE 1=1"
        params: List[Any] = []
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if primary_muscle:
            query += " AND primary_muscle = ?"
            params.append(PRIMARY_MUSCLE_LABELS.get(primary_muscle, primary_muscle))
        if equipment:
            query += " AND equipment = ?"
            params.append(EQUIPMENT_LABELS.get(equipment, equipment))
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_exercise(row) for row in rows if row]

    def update(self, exercise: Exercise) -> None:
        now = int(time.time())
        data = (
            exercise.name,
            exercise.slug,
            PRIMARY_MUSCLE_LABELS.get(exercise.primary_muscle),
            json.dumps([
                PRIMARY_MUSCLE_LABELS.get(m) for m in exercise.secondary_muscles
            ])
            if exercise.secondary_muscles
            else None,
            EQUIPMENT_LABELS.get(exercise.equipment) if exercise.equipment else None,
            PATTERN_LABELS.get(exercise.pattern) if exercise.pattern else None,
            exercise.difficulty,
            exercise.tempo,
            exercise.rep_range,
            exercise.rpe_default,
            exercise.rest_s_default,
            exercise.cues,
            exercise.image_path,
            exercise.is_active,
            now,
            exercise.id,
        )
        with self.conn:
            self.conn.execute(
                """
                UPDATE exercises SET
                    name=?, slug=?, primary_muscle=?, secondary_muscles=?, equipment=?,
                    pattern=?, difficulty=?, tempo=?, rep_range=?, rpe_default=?,
                    rest_s_default=?, cues=?, image_path=?, is_active=?, updated_at=?
                WHERE id=?
                """,
                data,
            )

    def soft_delete(self, exercise_id: str) -> None:
        now = int(time.time())
        with self.conn:
            self.conn.execute(
                "UPDATE exercises SET is_active = 0, updated_at = ? WHERE id = ?",
                (now, exercise_id),
            )

    def is_used_in_session(self, exercise_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM session_exercises WHERE exercise_id = ? LIMIT 1",
            (exercise_id,),
        ).fetchone()
        return row is not None

    # --- search --------------------------------------------------
    def search(
        self,
        *,
        query: str = "",
        primary_muscles: List[str] | None = None,
        equipment: List[str] | None = None,
        patterns: List[str] | None = None,
        difficulty: tuple[int, int] | None = None,
        include_inactive: bool = False,
    ) -> List[Exercise]:
        sql = "SELECT * FROM exercises WHERE 1=1"
        params: List[Any] = []
        if query:
            q = f"%{self._normalize(query)}%"
            sql += " AND (normalize(name) LIKE ? OR normalize(cues) LIKE ?)"
            params.extend([q, q])
        if primary_muscles:
            placeholders = ",".join("?" * len(primary_muscles))
            sql += f" AND primary_muscle IN ({placeholders})"
            params.extend([PRIMARY_MUSCLE_LABELS[m] for m in primary_muscles])
        if equipment:
            placeholders = ",".join("?" * len(equipment))
            sql += f" AND equipment IN ({placeholders})"
            params.extend([EQUIPMENT_LABELS[e] for e in equipment])
        if patterns:
            placeholders = ",".join("?" * len(patterns))
            sql += f" AND pattern IN ({placeholders})"
            params.extend([PATTERN_LABELS[p] for p in patterns])
        if difficulty:
            sql += " AND difficulty BETWEEN ? AND ?"
            params.extend([difficulty[0], difficulty[1]])
        if not include_inactive:
            sql += " AND is_active = 1"
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_exercise(r) for r in rows if r]

    # helper normalization
    @staticmethod
    def _normalize(text: str | None) -> str:
        if not text:
            return ""
        return (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
            .lower()
        )


__all__ = ["ExercisesRepository"]
