"""Base page class for all application pages."""
from __future__ import annotations

import customtkinter as ctk

from services.store import AppState, Store


class BasePage(ctk.CTkScrollableFrame):
    """Common page behaviour with access to router and store."""

    def __init__(self, master: ctk.CTkFrame, router, store: Store[AppState], **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.router = router
        self.store = store

    @property
    def breadcrumb(self) -> list[str]:
        """Return breadcrumb path for header."""
        return []
