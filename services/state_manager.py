"""Central state management using the observable pattern.

This module exposes a :class:`Store` singleton that holds the immutable
application state and allows external components to subscribe to state
changes.  The store implements a simple observer pattern where observers are
notified whenever the state is updated.
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
    current_view:
        Name of the view currently displayed in the application.
    """

    current_view: str = "home"


class Store:
    """Singleton store managing application state and observers.

    The store exposes methods to retrieve and update the state and to
    register or remove observers.  Observers are callables invoked whenever
    the state changes.
    """

    _instance: Store | None = None

    def __init__(self) -> None:
        self._state: AppState = AppState()
        self._observers: List[Callable[[AppState], None]] = []

    @classmethod
    def get_instance(cls) -> "Store":
        """Return the unique :class:`Store` instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_state(self) -> AppState:
        """Return a deep copy of the current application state."""
        return deepcopy(self._state)

    def set_state(self, new_state: AppState) -> None:
        """Update the application state and notify observers if it changes.

        Parameters
        ----------
        new_state:
            The new immutable state to replace the current one.
        """

        if new_state != self._state:
            self._state = new_state
            self.notify(self.get_state())

    def subscribe(self, observer: Callable[[AppState], None]) -> None:
        """Register an observer to be notified on state updates."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Callable[[AppState], None]) -> None:
        """Remove an observer from the notification list."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, new_state: AppState) -> None:
        """Notify all observers with the provided state.

        Parameters
        ----------
        new_state:
            The state to send to each observer.  It is typically a copy
            returned from :meth:`get_state` to prevent accidental
            modification.
        """

        for observer in list(self._observers):
            observer(new_state)


__all__ = ["AppState", "Store"]

