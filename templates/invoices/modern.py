"""Modern invoice PDF template with accent color."""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfgen import canvas as canvas_module

from services.pdf_exporter import Branding


def render(c: canvas_module.Canvas, data: dict, branding: Branding) -> None:
    """Render invoice using a modern layout."""
    invoice = data["invoice"]
    width, height = c._pagesize
    accent = colors.HexColor(branding.accent_color)
    c.setFillColor(accent)
    c.rect(0, height - 60, width, 60, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(c._fontname, 14)
    c.drawString(40, height - 40, f"Facture {invoice.number}")
    c.setFillColor(colors.black)
    y = height - 100
    c.drawString(40, y, f"Client : {data.get('client_name', '')}")
    y -= 20
    c.drawString(40, y, f"{invoice.label}")
    y -= 20
    amount = invoice.amount_cents / 100
    c.setFillColor(accent)
    c.drawString(40, y, f"Total : {amount:.2f} €")
    y -= 40
    c.setFillColor(colors.black)
    c.drawString(40, y, data.get("mentions", ""))
