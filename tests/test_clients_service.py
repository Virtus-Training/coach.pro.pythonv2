from unittest.mock import MagicMock
from datetime import date, timedelta
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.client import Client
from services.clients_service import ClientsService


def valid_data():
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "sex": "Femme",
        "birthdate": date(1995, 5, 20),
        "email": "jane@example.com",
        "phone": "555",
        "height_cm": 170.0,
        "weight_kg": 60.0,
    }


def test_create_update_delete():
    repo = MagicMock()
    repo.get_by_identity.return_value = None
    service = ClientsService(repo)
    client = service.create(valid_data())
    repo.add.assert_called_once()
    repo.get.return_value = client
    repo.get_by_identity.return_value = None
    updated = service.update(client.id, {"first_name": "Janette"})
    assert updated.first_name == "Janette"
    repo.update.assert_called()
    repo.get.return_value = client
    service.delete(client.id)
    repo.update.assert_called()
    repo.delete.assert_called_once_with(client.id)


def test_create_duplicate():
    repo = MagicMock()
    repo.get_by_identity.return_value = Client(
        id="1",
        first_name="Jane",
        last_name="Doe",
        sex="Femme",
        birthdate=date(1995, 5, 20),
        email="jane@example.com",
        phone="555",
    )
    service = ClientsService(repo)
    with pytest.raises(ValueError):
        service.create(valid_data())


def test_update_errors():
    repo = MagicMock()
    service = ClientsService(repo)
    repo.get.return_value = None
    with pytest.raises(ValueError):
        service.update("missing", {})
    existing = Client(
        id="1",
        first_name="John",
        last_name="Doe",
        sex="Homme",
        birthdate=date(1990, 1, 1),
        email="john@example.com",
        phone="111",
    )
    repo.get.return_value = existing
    repo.get_by_identity.return_value = Client(
        id="2",
        first_name="Jane",
        last_name="Doe",
        sex="Femme",
        birthdate=date(1990, 1, 1),
        email="jane@example.com",
        phone="222",
    )
    with pytest.raises(ValueError):
        service.update("1", {"first_name": "Jane"})


def test_validation_errors():
    repo = MagicMock()
    repo.get_by_identity.return_value = None
    service = ClientsService(repo)
    bad = valid_data()
    bad["sex"] = "X"
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad["birthdate"] = date.today() + timedelta(days=1)
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad["email"] = ""
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad["height_cm"] = -1
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data()
    bad["weight_kg"] = 0
    with pytest.raises(ValueError):
        service.create(bad)
