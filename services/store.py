"""Global observable store for application state."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Generic, List, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class ExerciseFilters:
    """Filters applied to exercise listings."""

    primary_muscles: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    difficulty_min: int = 1
    difficulty_max: int = 5


@dataclass(frozen=True)
class ExercisesState:
    """State related to exercises catalogue."""

    search_query: str = ""
    active_filters: ExerciseFilters = field(default_factory=ExerciseFilters)
    include_inactive: bool = False


@dataclass(frozen=True)
class AppState:
    """Immutable application state."""

    route: str = "home"
    exercises: ExercisesState = field(default_factory=ExercisesState)


class Store(Generic[T]):
    """Observable store maintaining application state."""

    def __init__(self, initial_state: T) -> None:
        self._state: T = initial_state
        self._subscribers: List[Callable[[T], None]] = []

    def get_state(self) -> T:
        """Return current state."""
        return self._state

    def subscribe(self, callback: Callable[[T], None]) -> None:
        """Subscribe to state changes."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[T], None]) -> None:
        """Unsubscribe from state changes."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify(self) -> None:
        for callback in list(self._subscribers):
            callback(self._state)

    def set_state(self, new_state: T) -> None:
        """Update state immutably and notify subscribers."""
        self._state = new_state
        self._notify()

    def update(self, **changes) -> None:
        """Convenience method to update dataclass fields."""
        if not hasattr(self._state, "__dataclass_fields"):
            raise TypeError("State must be a dataclass to use update().")
        self.set_state(replace(self._state, **changes))
