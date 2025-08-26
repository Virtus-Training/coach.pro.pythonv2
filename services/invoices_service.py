"""Business logic for managing invoices."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List, Optional

from models.invoice import Invoice
from repositories.invoices_repository import InvoicesRepository
from services.pdf_exporter import PDFExporter
from repositories.clients_repository import ClientsRepository

ALLOWED_STATUS = {"Payée", "Non payée"}
ALLOWED_TEMPLATES = {"classic", "modern", "minimalist"}


class InvoicesService:
    """Service layer that validates data and interacts with repository."""

    def __init__(
        self,
        repo: InvoicesRepository,
        clients_repo: Optional[ClientsRepository] = None,
        pdf_exporter: Optional[PDFExporter] = None,
    ) -> None:
        self.repo = repo
        self.clients_repo = clients_repo
        self.pdf_exporter = pdf_exporter or PDFExporter()

    # ------------------------------------------------------------------
    def create(self, data: Dict[str, object]) -> Invoice:
        """Create a new invoice with automatic numbering."""
        self._validate(data, creating=True)
        issued_on: date = data.get("issued_on") or date.today()
        year = issued_on.year
        last_number = self.repo.get_last_number(year)
        seq = 1
        if last_number:
            seq = int(last_number.split("-")[1]) + 1
        number = f"{year}-{seq:03d}"
        invoice = Invoice(
            id=str(uuid.uuid4()),
            client_id=data.get("client_id"),
            number=number,
            label=data.get("label"),
            amount_cents=int(data["amount_cents"]),
            status="Non payée",
            issued_on=issued_on,
            template=data.get("template", "classic"),
        )
        self.repo.add(invoice)
        return invoice

    def get(self, invoice_id: str) -> Optional[Invoice]:
        return self.repo.get(invoice_id)

    def list_all(self) -> List[Invoice]:
        return self.repo.list_all()

    def update(self, invoice_id: str, data: Dict[str, object]) -> Invoice:
        existing = self.repo.get(invoice_id)
        if not existing:
            raise ValueError("Invoice not found")
        merged = existing.__dict__ | data
        self._validate(merged, creating=False, existing=existing)
        status = merged.get("status", existing.status)
        paid_on = existing.paid_on
        if existing.status == "Non payée" and status == "Payée":
            paid_on = date.today()
        elif existing.status == "Payée" and status != "Payée":
            raise ValueError("Paid invoice status cannot be changed")
        if "paid_on" in data and existing.paid_on:
            raise ValueError("paid_on cannot be modified")
        updated = Invoice(
            id=existing.id,
            client_id=merged.get("client_id"),
            number=existing.number,
            label=merged.get("label"),
            amount_cents=int(merged.get("amount_cents", existing.amount_cents)),
            status=status,
            issued_on=merged.get("issued_on", existing.issued_on),
            paid_on=paid_on,
            pdf_path=merged.get("pdf_path", existing.pdf_path),
            template=merged.get("template", existing.template),
        )
        self.repo.update(updated)
        return updated

    def delete(self, invoice_id: str) -> None:
        self.repo.delete(invoice_id)

    def generate_pdf(self, invoice_id: str, branding: Dict[str, str]) -> str:
        invoice = self.repo.get(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        client_name = "client"
        if invoice.client_id and self.clients_repo:
            client = self.clients_repo.get(invoice.client_id)
            if client:
                client_name = f"{client.first_name}_{client.last_name}"
        output_name = f"invoice_{invoice.number}_{client_name}.pdf"
        output_path = f"exports/invoices/{output_name}"
        data = {
            "document_title": f"Facture {invoice.number}",
            "invoice": invoice,
            "client_name": client_name.replace("_", " "),
            "mentions": "TVA non applicable, art. 293B du CGI",
        }
        path = self.pdf_exporter.generate(
            f"invoices.{invoice.template}", data, output_path, branding
        )
        invoice.pdf_path = path
        self.repo.update(invoice)
        return path

    # ------------------------------------------------------------------
    def _validate(
        self,
        data: Dict[str, object],
        creating: bool,
        existing: Optional[Invoice] = None,
    ) -> None:
        if creating:
            required = ["amount_cents"]
            for field in required:
                if data.get(field) is None:
                    raise ValueError(f"{field} is required")
        amount = int(data.get("amount_cents", 0))
        if amount < 0:
            raise ValueError("amount_cents must be non-negative")
        status = data.get("status") or (existing.status if existing else "Non payée")
        if status not in ALLOWED_STATUS:
            raise ValueError("Invalid status")
        template = data.get("template") or (existing.template if existing else "classic")
        if template not in ALLOWED_TEMPLATES:
            raise ValueError("Invalid template")


__all__ = ["InvoicesService"]
