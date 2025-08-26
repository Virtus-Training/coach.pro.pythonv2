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
        "height_cm": 170.0,
        "weight_kg": 60.0,
        "email": "jane@example.com",
        "phone": "555",
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
    anon_client = repo.update.call_args[0][0]
    assert anon_client.first_name == "Anonyme"
    assert anon_client.email is None
    repo.delete.assert_called_once_with(client.id)


def test_create_duplicate():
    repo = MagicMock()
    repo.get_by_identity.return_value = Client(
        id="1",
        first_name="Jane",
        last_name="Doe",
        sex="Femme",
        birthdate=date(1995, 5, 20),
        height_cm=170.0,
        weight_kg=60.0,
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
        height_cm=180.0,
        weight_kg=80.0,
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
        height_cm=165.0,
        weight_kg=60.0,
        email="jane@example.com",
        phone="222",
    )
    with pytest.raises(ValueError):
        service.update("1", {"first_name": "Jane"})


def test_validation_errors():
    repo = MagicMock()
    repo.get_by_identity.return_value = None
    service = ClientsService(repo)
    bad = valid_data(); bad["sex"] = "X"; 
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data(); bad["birthdate"] = date.today() + timedelta(days=1)
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data(); del bad["first_name"]
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data(); bad["height_cm"] = -1
    with pytest.raises(ValueError):
        service.create(bad)
    bad = valid_data(); del bad["weight_kg"]
    with pytest.raises(ValueError):
        service.create(bad)


def test_create_without_contact_info():
    repo = MagicMock()
    repo.get_by_identity.return_value = None
    service = ClientsService(repo)
    data = valid_data()
    del data["email"]
    del data["phone"]
    client = service.create(data)
    assert client.email is None
    repo.add.assert_called_once()


def test_delete_missing_client():
    repo = MagicMock()
    repo.get.return_value = None
    service = ClientsService(repo)
    with pytest.raises(ValueError):
        service.delete("missing")
