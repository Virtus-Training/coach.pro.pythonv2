from unittest.mock import MagicMock
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.exercise import Exercise
from services.exercises_service import ExercisesService


def valid_data():
    return {
        'name': 'Développé couché',
        'primary_muscle': 'PECTORAUX',
        'secondary_muscles': ['TRICEPS'],
        'equipment': 'BAR',
        'pattern': 'PH',
        'difficulty': 3,
        'rpe_default': 7.5,
        'rest_s_default': 120,
    }


def test_create_success_and_slug():
    repo = MagicMock()
    repo.get_by_name.return_value = None
    service = ExercisesService(repo)
    ex = service.create(valid_data())
    assert ex.slug == 'developpe-couche'
    repo.create.assert_called_once()


def test_create_duplicate_name():
    repo = MagicMock()
    repo.get_by_name.return_value = Exercise(id='1', name='x', slug='x', primary_muscle='PECTORAUX')
    service = ExercisesService(repo)
    with pytest.raises(ValueError):
        service.create(valid_data())


def test_validation_errors():
    repo = MagicMock()
    repo.get_by_name.return_value = None
    service = ExercisesService(repo)
    bad = valid_data()
    bad['difficulty'] = 8
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad['primary_muscle'] = 'INVALID'
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad['equipment'] = 'INVALID'
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad['pattern'] = 'INVALID'
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad['rpe_default'] = 11
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad['rest_s_default'] = -5
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad['secondary_muscles'] = 'TRICEPS'
    with pytest.raises(ValueError):
        service.create(bad)


def test_update_and_soft_delete():
    repo = MagicMock()
    existing = Exercise(id='1', name='Old', slug='old', primary_muscle='PECTORAUX')
    repo.get_by_id.side_effect = [existing, existing, None]
    repo.get_by_name.return_value = None
    service = ExercisesService(repo)
    updated = service.update('1', {'name': 'Nouveau', 'difficulty': 4})
    assert updated.name == 'Nouveau'
    repo.update.assert_called_once()
    repo.get_by_name.return_value = Exercise(id='2', name='Nouveau', slug='n', primary_muscle='PECTORAUX')
    with pytest.raises(ValueError):
        service.update('1', {'name': 'Nouveau'})
    with pytest.raises(ValueError):
        service.update('missing', {})
    # soft delete behaviour
    repo.is_used_in_session.return_value = True
    with pytest.raises(ValueError):
        service.soft_delete('1')
    repo.is_used_in_session.return_value = False
    service.soft_delete('1')
    repo.soft_delete.assert_called_once_with('1')
    service.list_all(name='test')
    repo.list_all.assert_called_once()
