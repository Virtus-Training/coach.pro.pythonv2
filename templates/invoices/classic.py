"""Classic invoice PDF template."""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as canvas_module

from services.pdf_exporter import Branding


def render(c: canvas_module.Canvas, data: dict, branding: Branding) -> None:
    """Render invoice using a classic layout."""
    invoice = data["invoice"]
    width, height = c._pagesize
    x_margin, y = 40, height - 80
    c.setFont(c._fontname, 12)
    c.drawString(x_margin, y, f"Facture n° {invoice.number}")
    y -= 20
    c.drawString(x_margin, y, f"Émise le {invoice.issued_on.isoformat()}")
    y -= 40
    c.drawString(x_margin, y, f"Client : {data.get('client_name', '')}")
    y -= 20
    c.drawString(x_margin, y, f"{invoice.label}")
    y -= 20
    amount = invoice.amount_cents / 100
    c.drawString(x_margin, y, f"Montant : {amount:.2f} €")
    y -= 40
    c.setFillColor(colors.black)
    c.drawString(x_margin, y, data.get("mentions", ""))
