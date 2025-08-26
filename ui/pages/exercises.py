"""Exercises page placeholder."""
from __future__ import annotations

import customtkinter as ctk

from config.enums import PRIMARY_MUSCLE_LABELS
from services.exercises_service import ExercisesService
from services.store import AppState, Store
from ui.base_page import BasePage
from ui.widgets.exercise_filters import ExerciseFiltersWidget


class ExercisesPage(BasePage):
    """Placeholder for exercises page."""

    def __init__(
        self,
        master: ctk.CTkFrame,
        router,
        store: Store[AppState],
        service: ExercisesService,
        **kwargs,
    ) -> None:
        super().__init__(master, router, store, **kwargs)
        self.service = service
        self.store.subscribe(self._on_state_change)

        self.filters = ExerciseFiltersWidget(self, store)
        self.filters.pack(side="left", fill="y")

        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(side="right", fill="both", expand=True)

        self._on_state_change(self.store.get_state())

    @property
    def breadcrumb(self) -> list[str]:
        return ["Exercices"]

    def _on_state_change(self, state: AppState) -> None:
        ex_state = state.exercises
        results = self.service.search(
            query=ex_state.search_query,
            primary_muscles=ex_state.active_filters.primary_muscles,
            equipment=ex_state.active_filters.equipment,
            patterns=ex_state.active_filters.patterns,
            difficulty=(
                ex_state.active_filters.difficulty_min,
                ex_state.active_filters.difficulty_max,
            ),
            include_inactive=ex_state.include_inactive,
        )
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        if not results:
            ctk.CTkLabel(self.list_frame, text="Aucun résultat").pack(padx=20, pady=20)
            return
        for ex in results:
            label = f"{ex.name} - {PRIMARY_MUSCLE_LABELS.get(ex.primary_muscle, ex.primary_muscle)}"
            ctk.CTkLabel(self.list_frame, text=label).pack(anchor="w", padx=10, pady=2)
