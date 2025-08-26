from unittest.mock import MagicMock
from datetime import date
import sys
from pathlib import Path
from unittest.mock import MagicMock
from datetime import date

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.invoice import Invoice
from services.invoices_service import InvoicesService


def test_numbering_and_status():
    repo = MagicMock()
    repo.get_last_number.side_effect = [None, "2024-001", None]
    service = InvoicesService(repo, pdf_exporter=MagicMock())
    inv1 = service.create({"amount_cents": 1000, "issued_on": date(2024, 1, 1)})
    inv2 = service.create({"amount_cents": 1000, "issued_on": date(2024, 6, 1)})
    inv3 = service.create({"amount_cents": 1000, "issued_on": date(2025, 1, 1)})
    assert inv1.number == "2024-001"
    assert inv2.number == "2024-002"
    assert inv3.number == "2025-001"
    assert inv1.status == "Non payée"


def test_status_update_and_lock():
    repo = MagicMock()
    service = InvoicesService(repo, pdf_exporter=MagicMock())
    existing = Invoice(
        id="1",
        client_id=None,
        number="2024-001",
        label="Coaching",
        amount_cents=1000,
        status="Non payée",
        issued_on=date(2024, 1, 1),
        template="classic",
    )
    repo.get.return_value = existing
    today = date.today()
    inv = service.update("1", {"status": "Payée"})
    assert inv.status == "Payée"
    assert inv.paid_on == today
    repo.get.return_value = inv
    with pytest.raises(ValueError):
        service.update("1", {"paid_on": today})
    with pytest.raises(ValueError):
        service.update("1", {"status": "Non payée"})


def test_generate_pdf_updates_path():
    repo = MagicMock()
    client_repo = MagicMock()
    client_repo.get.return_value = MagicMock(first_name="John", last_name="Doe")
    exporter = MagicMock()
    invoice = Invoice(
        id="1",
        client_id="c1",
        number="2024-001",
        label="Coaching",
        amount_cents=1000,
        status="Non payée",
        issued_on=date(2024, 1, 1),
        template="classic",
    )
    repo.get.return_value = invoice
    exporter.generate.return_value = "exports/invoices/invoice_2024-001_John_Doe.pdf"
    service = InvoicesService(repo, client_repo, exporter)
    path = service.generate_pdf("1", {"name": "Coach", "accent_color": "#000", "primary_color": "#000", "secondary_color": "#000", "contact_email": "", "contact_phone": ""})
    assert path == invoice.pdf_path
    exporter.generate.assert_called_once()
    repo.update.assert_called_once()
