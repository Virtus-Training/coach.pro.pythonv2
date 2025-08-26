"""Simple string-based router for navigation between pages."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, Optional, Type

import customtkinter as ctk

from services.store import AppState, Store
from ui.base_page import BasePage
from ui.header import Header


class Router:
    """Manage navigation and page lifecycle."""

    def __init__(self, container: ctk.CTkFrame, store: Store[AppState], header: Header) -> None:
        self._container = container
        self._store = store
        self._header = header
        self._routes: Dict[str, Type[BasePage]] = {}
        self._current_page: Optional[BasePage] = None

    def register(self, route: str, page: Type[BasePage]) -> None:
        """Register a route name to a page class."""
        self._routes[route] = page

    def navigate(self, route: str) -> None:
        """Navigate to a page by its route name."""
        if route not in self._routes:
            raise ValueError(f"Route '{route}' is not registered.")

        if self._current_page is not None:
            self._current_page.destroy()

        page_class = self._routes[route]
        self._current_page = page_class(self._container, self, self._store)
        self._current_page.grid(row=0, column=0, sticky="nsew")
        self._header.update_breadcrumb(self._current_page.breadcrumb)
        self._store.set_state(replace(self._store.get_state(), route=route))
