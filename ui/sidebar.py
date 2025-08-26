"""Sidebar navigation component."""
from __future__ import annotations

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """Vertical sidebar with navigation buttons."""

    def __init__(self, master: ctk.CTkFrame, router, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.router = router
        self.grid_rowconfigure(len(self._buttons_info()) + 1, weight=1)
        for row, (icon, label, route) in enumerate(self._buttons_info()):
            btn = ctk.CTkButton(
                self,
                text=f"{icon} {label}",
                anchor="w",
                command=lambda r=route: self.router.navigate(r),
            )
            btn.grid(row=row, column=0, sticky="ew", padx=5, pady=5)

    def _buttons_info(self) -> list[tuple[str, str, str]]:
        return [
            ("🏠", "Accueil", "home"),
            ("🏋️", "Exercices", "exercises"),
            ("📆", "Séances", "sessions"),
            ("⚙", "Paramètres", "settings"),
        ]
