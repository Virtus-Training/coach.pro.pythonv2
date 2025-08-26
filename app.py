"""Application entry point for Virtus Training."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from controllers.router import Router
from services.store import AppState, Store
from ui.header import Header
from ui.sidebar import Sidebar
from ui.pages.home import HomePage
from ui.pages.exercises import ExercisesPage
from ui.pages.sessions import SessionsPage
from ui.pages.settings import SettingsPage


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> None:
    """Configure application logging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
    )


def handle_exception(exc_type, exc_value, exc_traceback) -> None:  # type: ignore[override]
    """Global exception handler."""
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror("Erreur", str(exc_value))


class App(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        super().__init__()
        self.title("Virtus Training")
        self.geometry("900x600")
        self.minsize(800, 500)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.store = Store(AppState())

        self.header = Header(self)
        self.header.grid(row=0, column=1, sticky="ew")

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.router = Router(self.content, self.store, self.header)
        self.sidebar = Sidebar(self, self.router, width=150)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")

        self._register_routes()
        self.router.navigate("home")

    def _register_routes(self) -> None:
        self.router.register("home", HomePage)
        self.router.register("exercises", ExercisesPage)
        self.router.register("sessions", SessionsPage)
        self.router.register("settings", SettingsPage)


def main() -> None:
    """Application bootstrap."""
    setup_logging()
    sys.excepthook = handle_exception
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
