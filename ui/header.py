"""Header containing breadcrumb navigation."""
from __future__ import annotations

import customtkinter as ctk


class Header(ctk.CTkFrame):
    """Application header with breadcrumb."""

    def __init__(self, master: ctk.CTkFrame, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self._breadcrumb = ctk.CTkLabel(self, text="Accueil", anchor="w")
        self._breadcrumb.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def update_breadcrumb(self, path: list[str]) -> None:
        """Update breadcrumb display."""
        self._breadcrumb.configure(text=" > ".join(path))
