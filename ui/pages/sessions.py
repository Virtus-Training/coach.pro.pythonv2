"""Sessions page placeholder."""
from __future__ import annotations

import customtkinter as ctk

from services.store import AppState, Store
from ui.base_page import BasePage


class SessionsPage(BasePage):
    """Placeholder for sessions page."""

    def __init__(self, master: ctk.CTkFrame, router, store: Store[AppState], **kwargs) -> None:
        super().__init__(master, router, store, **kwargs)
        ctk.CTkLabel(self, text="Séances").pack(padx=20, pady=20)

    @property
    def breadcrumb(self) -> list[str]:
        return ["Séances"]
