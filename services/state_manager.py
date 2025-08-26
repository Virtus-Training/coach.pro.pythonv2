"""Global state management with observer pattern.

This module defines a ``Store`` class that acts as the single source of
truth for the application's state. The store follows the Singleton
pattern and implements a simple observable mechanism allowing external
components to subscribe to state updates.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, List


@dataclass(frozen=True)
class AppState:
    """Immutable application state.

    Attributes
    ----------
    current_view: str
        Name of the view currently displayed in the application.
    """

    current_view: str = "home"


class Store:
    """Singleton store managing application state and observers."""

    _instance: Store | None = None

    def __new__(cls) -> Store:  # type: ignore[override]
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers: List[Callable[[AppState], None]] = []
            cls._instance._state: AppState = AppState()
        return cls._instance

    def get_state(self) -> AppState:
        """Return a deep copy of the current state."""
        return deepcopy(self._state)

    def set_state(self, new_state: AppState) -> None:
        """Replace the current state and notify observers if it changed."""
        if new_state != self._state:
            self._state = new_state
            self.notify()

    def subscribe(self, observer: Callable[[AppState], None]) -> None:
        """Register an observer for state updates."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Callable[[AppState], None]) -> None:
        """Remove an observer from state updates."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self) -> None:
        """Notify all observers with the updated state."""
        state_copy = self.get_state()
        for observer in list(self._observers):
            observer(state_copy)
