from datetime import date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.invoice import Invoice
from services.pdf_exporter import PDFExporter


def test_templates_generate(tmp_path):
    exporter = PDFExporter(font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    invoice = Invoice(
        id="1",
        client_id=None,
        number="2024-001",
        label="Coaching",
        amount_cents=1000,
        status="Non payée",
        issued_on=date.today(),
        template="classic",
    )
    data = {
        "document_title": "Facture",
        "invoice": invoice,
        "client_name": "John Doe",
        "mentions": "TVA non applicable, art. 293B du CGI",
    }
    branding = {
        "name": "Coach",
        "logo_path": None,
        "primary_color": "#000000",
        "secondary_color": "#000000",
        "accent_color": "#000000",
        "contact_email": "",
        "contact_phone": "",
    }
    for tpl in ["classic", "modern", "minimalist"]:
        path = tmp_path / f"{tpl}.pdf"
        exporter.generate(f"invoices.{tpl}", data, str(path), branding)
        assert path.exists()
