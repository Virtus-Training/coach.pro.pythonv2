from __future__ import annotations

"""Widget encapsulating search and filter controls for exercises."""

import tkinter as tk
import customtkinter as ctk

from config.enums import (
    PRIMARY_MUSCLE_LABELS,
    EQUIPMENT_LABELS,
    PATTERN_LABELS,
)
from services.store import Store, AppState, ExerciseFilters, ExercisesState


class ExerciseFiltersWidget(ctk.CTkFrame):
    """UI widget allowing user to search and filter exercises."""

    def __init__(self, master: ctk.CTkFrame, store: Store[AppState], **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.store = store

        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(self, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=5, pady=5)
        search_entry.bind("<KeyRelease>", self._on_change)

        # Checkboxes for primary muscles
        self.primary_vars: dict[str, tk.BooleanVar] = {}
        pm_frame = ctk.CTkScrollableFrame(self, height=120)
        pm_frame.pack(fill="x", padx=5, pady=5)
        for code, label in PRIMARY_MUSCLE_LABELS.items():
            var = tk.BooleanVar()
            self.primary_vars[code] = var
            ctk.CTkCheckBox(pm_frame, text=label, variable=var, command=self._on_change).pack(anchor="w")

        # Equipment checkboxes
        self.equipment_vars: dict[str, tk.BooleanVar] = {}
        eq_frame = ctk.CTkScrollableFrame(self, height=80)
        eq_frame.pack(fill="x", padx=5, pady=5)
        for code, label in EQUIPMENT_LABELS.items():
            var = tk.BooleanVar()
            self.equipment_vars[code] = var
            ctk.CTkCheckBox(eq_frame, text=label, variable=var, command=self._on_change).pack(anchor="w")

        # Pattern checkboxes
        self.pattern_vars: dict[str, tk.BooleanVar] = {}
        pat_frame = ctk.CTkScrollableFrame(self, height=80)
        pat_frame.pack(fill="x", padx=5, pady=5)
        for code, label in PATTERN_LABELS.items():
            var = tk.BooleanVar()
            self.pattern_vars[code] = var
            ctk.CTkCheckBox(pat_frame, text=label, variable=var, command=self._on_change).pack(anchor="w")

        # Difficulty sliders
        self.diff_min = tk.IntVar(value=1)
        self.diff_max = tk.IntVar(value=5)
        diff_frame = ctk.CTkFrame(self)
        diff_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(diff_frame, text="Difficulté").pack(anchor="w")
        ctk.CTkSlider(diff_frame, from_=1, to=5, variable=self.diff_min, command=lambda v: self._on_change()).pack(fill="x")
        ctk.CTkSlider(diff_frame, from_=1, to=5, variable=self.diff_max, command=lambda v: self._on_change()).pack(fill="x")

        # Include inactive
        self.inactive_var = tk.BooleanVar()
        ctk.CTkCheckBox(self, text="Inclure les inactifs", variable=self.inactive_var, command=self._on_change).pack(anchor="w", padx=5, pady=5)

    def _on_change(self, event: tk.Event | None = None) -> None:
        filters = ExerciseFilters(
            primary_muscles=[code for code, var in self.primary_vars.items() if var.get()],
            equipment=[code for code, var in self.equipment_vars.items() if var.get()],
            patterns=[code for code, var in self.pattern_vars.items() if var.get()],
            difficulty_min=self.diff_min.get(),
            difficulty_max=self.diff_max.get(),
        )
        new_state = ExercisesState(
            search_query=self.search_var.get(),
            active_filters=filters,
            include_inactive=self.inactive_var.get(),
        )
        self.store.update(exercises=new_state)


__all__ = ["ExerciseFiltersWidget"]
