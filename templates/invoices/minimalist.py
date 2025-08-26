"""Minimalist black and white invoice PDF template."""
from __future__ import annotations

from reportlab.pdfgen import canvas as canvas_module

from services.pdf_exporter import Branding


def render(c: canvas_module.Canvas, data: dict, branding: Branding) -> None:
    """Render invoice using a minimalist layout."""
    invoice = data["invoice"]
    width, height = c._pagesize
    c.setFont(c._fontname, 12)
    y = height - 80
    c.drawString(40, y, f"Facture {invoice.number}")
    y -= 20
    c.drawString(40, y, f"Client : {data.get('client_name', '')}")
    y -= 20
    c.drawString(40, y, f"{invoice.label}")
    y -= 20
    amount = invoice.amount_cents / 100
    c.drawString(40, y, f"Montant : {amount:.2f} €")
    y -= 40
    c.drawString(40, y, data.get("mentions", ""))
