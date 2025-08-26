"""Business logic for managing exercises."""
from __future__ import annotations

import re
import unicodedata
import uuid
from typing import Dict, List, Optional

from models.exercise import Exercise
from repositories.exercises_repository import ExercisesRepository

PRIMARY_MUSCLES = {
    'Pectoraux','Dorsaux','Épaules','Biceps','Triceps','Trapèzes','Lombaires',
    'Abdominaux','Obliques','Quadriceps','Ischio-jambiers','Fessiers','Mollets',
    'Avant-bras','Cou','Corps entier'
}
EQUIPMENTS = {
    'Barre','Haltères','Kettlebell','Poulie/Câble','Machine guidée','Smith',
    'Élastiques','TRX/Anneaux','Poids du corps','Banc/Step/Box','Swiss Ball',
    'Médecine ball','Sled/Prowler'
}
PATTERNS = {
    'Squat','Hinge','Fente','Push horizontal','Push vertical','Tirage horizontal',
    'Tirage vertical','Gainage','Anti-rotation','Rotation','Locomotion/Carry',
    'Saut/Pliométrie','Conditioning','Mobilité'
}


class ExercisesService:
    """Service layer that validates data and interacts with repository."""

    def __init__(self, repo: ExercisesRepository) -> None:
        self.repo = repo

    # ------------------------------------------------------------------
    def create(self, data: Dict[str, object]) -> Exercise:
        """Create a new exercise after validating input."""
        self._validate(data)
        if self.repo.get_by_name(data['name']):
            raise ValueError('Exercise name must be unique')
        exercise = Exercise(
            id=str(uuid.uuid4()),
            name=data['name'],
            slug=self._slugify(data['name']),
            primary_muscle=data['primary_muscle'],
            secondary_muscles=list(data.get('secondary_muscles', [])),
            equipment=data.get('equipment'),
            pattern=data.get('pattern'),
            difficulty=data.get('difficulty'),
            tempo=data.get('tempo'),
            rep_range=data.get('rep_range'),
            rpe_default=data.get('rpe_default'),
            rest_s_default=data.get('rest_s_default'),
            cues=data.get('cues'),
            image_path=data.get('image_path'),
        )
        self.repo.create(exercise)
        return exercise

    def update(self, exercise_id: str, data: Dict[str, object]) -> Exercise:
        """Update an existing exercise."""
        existing = self.repo.get_by_id(exercise_id)
        if not existing:
            raise ValueError('Exercise not found')
        new_name = data.get('name', existing.name)
        if new_name != existing.name and self.repo.get_by_name(new_name):
            raise ValueError('Exercise name must be unique')
        merged = existing.__dict__ | data
        self._validate(merged)
        updated = Exercise(
            id=existing.id,
            name=new_name,
            slug=self._slugify(new_name),
            primary_muscle=merged['primary_muscle'],
            secondary_muscles=list(merged.get('secondary_muscles', [])),
            equipment=merged.get('equipment'),
            pattern=merged.get('pattern'),
            difficulty=merged.get('difficulty'),
            tempo=merged.get('tempo'),
            rep_range=merged.get('rep_range'),
            rpe_default=merged.get('rpe_default'),
            rest_s_default=merged.get('rest_s_default'),
            cues=merged.get('cues'),
            image_path=merged.get('image_path'),
            is_active=merged.get('is_active', existing.is_active),
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )
        self.repo.update(updated)
        return updated

    def list_all(self, **filters: Optional[str]) -> List[Exercise]:
        """List exercises filtered by optional criteria."""
        return self.repo.list_all(
            name=filters.get('name'),
            primary_muscle=filters.get('primary_muscle'),
            equipment=filters.get('equipment'),
        )

    def soft_delete(self, exercise_id: str) -> None:
        """Soft delete an exercise if not used in sessions."""
        if self.repo.is_used_in_session(exercise_id):
            raise ValueError('Exercise is used in a session and cannot be deleted')
        self.repo.soft_delete(exercise_id)

    # ------------------------------------------------------------------
    def _validate(self, data: Dict[str, object]) -> None:
        if data['primary_muscle'] not in PRIMARY_MUSCLES:
            raise ValueError('Invalid primary muscle')
        equipment = data.get('equipment')
        if equipment and equipment not in EQUIPMENTS:
            raise ValueError('Invalid equipment')
        pattern = data.get('pattern')
        if pattern and pattern not in PATTERNS:
            raise ValueError('Invalid movement pattern')
        difficulty = data.get('difficulty')
        if difficulty is not None and not (1 <= int(difficulty) <= 5):
            raise ValueError('Difficulty must be between 1 and 5')
        rpe = data.get('rpe_default')
        if rpe is not None and not (0 <= float(rpe) <= 10):
            raise ValueError('RPE must be between 0 and 10')
        rest = data.get('rest_s_default')
        if rest is not None and int(rest) < 0:
            raise ValueError('Rest seconds must be >= 0')
        secondary = data.get('secondary_muscles')
        if secondary and not isinstance(secondary, list):
            raise ValueError('secondary_muscles must be a list of strings')

    @staticmethod
    def _slugify(value: str) -> str:
        """Return slugified version of ``value``."""
        norm = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        norm = re.sub(r"[^a-zA-Z0-9]+", "-", norm)
        return norm.strip('-').lower()


__all__ = ["ExercisesService"]
