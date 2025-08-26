"""Generic PDF export service using ReportLab.

This module exposes the :class:`PDFExporter` which loads template
functions dynamically and produces branded PDF documents.  Templates are
simple Python callables located under the :mod:`templates` package with
signature ``render(canvas, data, branding)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class PDFExportError(Exception):
    """Raised when the PDF generation process fails."""


@dataclass
class Branding:
    """Branding information injected into exported PDFs."""

    name: str
    logo_path: Optional[str]
    primary_color: str
    secondary_color: str
    accent_color: str
    contact_email: str
    contact_phone: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Branding":
        """Create :class:`Branding` from a dictionary, applying defaults."""

        return cls(
            name=data.get("name", ""),
            logo_path=data.get("logo_path"),
            primary_color=data.get("primary_color", "#000000"),
            secondary_color=data.get("secondary_color", "#000000"),
            accent_color=data.get("accent_color", "#000000"),
            contact_email=data.get("contact_email", ""),
            contact_phone=data.get("contact_phone", ""),
        )


class BrandedCanvas(canvas.Canvas):
    """Canvas subclass that draws header and footer on each page."""

    def __init__(
        self,
        filename: str,
        branding: Branding,
        document_title: str,
        pagesize: Iterable[float],
        font_name: str,
        **kwargs,
    ) -> None:
        super().__init__(filename, pagesize=pagesize, **kwargs)
        self._branding = branding
        self._document_title = document_title
        self._pagesize = pagesize
        self._font_name = font_name

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _draw_header_footer(self) -> None:
        width, height = self._pagesize
        margin = 40

        primary = colors.HexColor(self._branding.primary_color)
        accent = colors.HexColor(self._branding.accent_color)

        # Header background line
        self.setStrokeColor(accent)
        self.setFillColor(primary)

        # Logo or coach name on the left
        if self._branding.logo_path and Path(self._branding.logo_path).exists():
            try:
                self.drawImage(
                    self._branding.logo_path,
                    margin,
                    height - margin - 30,
                    width=60,
                    height=30,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                self.setFont(self._font_name, 12)
                self.drawString(margin, height - margin - 20, self._branding.name)
        else:
            self.setFont(self._font_name, 12)
            self.drawString(margin, height - margin - 20, self._branding.name)

        # Title centered
        self.setFont(self._font_name, 16)
        self.drawCentredString(width / 2, height - margin - 20, self._document_title)

        # Footer: page number and software branding
        self.setFont(self._font_name, 10)
        footer_y = margin / 2
        self.drawRightString(width - margin, footer_y, f"Page {self.getPageNumber()}")
        self.drawString(margin, footer_y, "Fiche personnalisée – Virtus Training")

    # ------------------------------------------------------------------
    # Canvas overrides
    # ------------------------------------------------------------------
    def showPage(self) -> None:  # noqa: D401 - inherit docstring
        self._draw_header_footer()
        super().showPage()

    def save(self) -> None:  # noqa: D401 - inherit docstring
        self._draw_header_footer()
        super().save()


class PDFExporter:
    """Service responsible for generating branded PDF documents."""

    def __init__(self, font_path: Optional[str] = None) -> None:
        """Initialise the exporter and register the Roboto font.

        Parameters
        ----------
        font_path:
            Optional path to a TrueType font to register.  Defaults to the
            bundled Roboto font.
        """

        font_path = font_path or str(Path("assets/fonts/Roboto-Regular.ttf"))
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont("Roboto", font_path))
            self._font_name = "Roboto"
        else:  # Fallback to a standard font if Roboto is missing
            self._font_name = "Helvetica"

    # ------------------------------------------------------------------
    def generate(
        self,
        template_name: str,
        data: Optional[Dict],
        output_path: str,
        branding: Dict[str, str],
    ) -> str:
        """Generate a PDF using the provided template and data.

        Parameters
        ----------
        template_name:
            Name of the template module under :mod:`templates` (e.g.
            ``"invoices.classic"``).
        data:
            Dictionary with content to render.  May be ``None``.
        output_path:
            Destination path for the generated PDF.
        branding:
            Branding information dictionary.

        Returns
        -------
        str
            Absolute path to the generated PDF file.

        Raises
        ------
        PDFExportError
            If the template cannot be loaded or rendering fails.
        """

        try:
            render_func = self._load_template(template_name)
            branding_obj = Branding.from_dict(branding)

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            pagesize = landscape(A4) if self._needs_landscape(data) else portrait(A4)
            document_title = (data or {}).get("document_title", "Document")

            canvas_obj = BrandedCanvas(
                str(output_file),
                branding=branding_obj,
                document_title=document_title,
                pagesize=pagesize,
                font_name=self._font_name,
            )

            if not data or not any(self._non_empty(v) for v in data.values()):
                width, height = pagesize
                canvas_obj.setFont(self._font_name, 14)
                canvas_obj.drawCentredString(
                    width / 2, height / 2, "Aucune donnée à afficher"
                )
            else:
                render_func(canvas_obj, data, branding_obj)

            canvas_obj.save()
            return str(output_file.resolve())
        except Exception as exc:  # pragma: no cover - rewrap exceptions
            raise PDFExportError(str(exc)) from exc

    # ------------------------------------------------------------------
    @staticmethod
    def _non_empty(value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        return True

    @staticmethod
    def _load_template(template_name: str) -> Callable[[canvas.Canvas, Dict, Branding], None]:
        module = import_module(f"templates.{template_name}")
        render_func = getattr(module, "render", None)
        if not callable(render_func):
            raise PDFExportError(f"Template '{template_name}' lacks a render function")
        return render_func

    @staticmethod
    def _needs_landscape(data: Optional[Dict]) -> bool:
        if not data:
            return False
        tables: List[List[List]] = []
        table = data.get("table")
        if isinstance(table, list):
            tables.append(table)
        multiple = data.get("tables")
        if isinstance(multiple, list):
            tables.extend(t for t in multiple if isinstance(t, list))

        for t in tables:
            if t and isinstance(t[0], (list, tuple)) and len(t[0]) > 5:
                return True
        return False


__all__ = ["PDFExporter", "PDFExportError"]
