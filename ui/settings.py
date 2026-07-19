"""Settings screen: sound, animations, theme, accent color, highlighting,
timer, and accessibility options. Every change is applied immediately and
persisted to disk through the storage module.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from assets.theme import THEMES


class SettingsScreen(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        settings: dict,
        on_change: Callable[[str, object], None],
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.settings = settings
        self.on_change = on_change
        self.on_back = on_back

        self.sound_var = tk.BooleanVar(value=settings["sound_enabled"])
        self.animations_var = tk.BooleanVar(value=settings["animations_enabled"])
        self.theme_var = tk.StringVar(value=settings["theme"])
        self.grid_highlight_var = tk.BooleanVar(value=settings["grid_highlight"])
        self.timer_var = tk.BooleanVar(value=settings["timer_enabled"])
        self.high_contrast_var = tk.BooleanVar(value=settings["high_contrast"])
        self.font_scale_var = tk.DoubleVar(value=settings["font_scale"])

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self)
        container.pack(expand=True, pady=40)

        ttk.Label(container, text="Settings", font=("Segoe UI", 24, "bold")).pack(pady=(0, 24))

        self._add_checkbox(container, "Sound Effects", self.sound_var, "sound_enabled")
        self._add_checkbox(container, "Animations", self.animations_var, "animations_enabled")
        self._add_checkbox(container, "Grid Highlighting", self.grid_highlight_var, "grid_highlight")
        self._add_checkbox(container, "Countdown Timer", self.timer_var, "timer_enabled")
        self._add_checkbox(container, "High Contrast Mode", self.high_contrast_var, "high_contrast")

        theme_row = ttk.Frame(container)
        theme_row.pack(fill="x", pady=8)
        ttk.Label(theme_row, text="Theme", width=20, anchor="w").pack(side="left")
        theme_menu = ttk.Combobox(
            theme_row, textvariable=self.theme_var, values=list(THEMES.keys()), state="readonly", width=14
        )
        theme_menu.pack(side="left")
        theme_menu.bind("<<ComboboxSelected>>", lambda e: self.on_change("theme", self.theme_var.get()))

        font_row = ttk.Frame(container)
        font_row.pack(fill="x", pady=8)
        ttk.Label(font_row, text="Font Size", width=20, anchor="w").pack(side="left")
        font_scale = ttk.Scale(
            font_row,
            from_=0.8,
            to=1.4,
            variable=self.font_scale_var,
            orient="horizontal",
            length=160,
            command=lambda v: self.on_change("font_scale", round(float(v), 2)),
        )
        font_scale.pack(side="left")

        shortcuts_frame = ttk.LabelFrame(container, text="Keyboard Shortcuts")
        shortcuts_frame.pack(fill="x", pady=(20, 10))
        shortcuts = [
            ("Arrow Keys", "Move selection"),
            ("1-9", "Enter a number"),
            ("Backspace / Delete", "Clear a cell"),
        ]
        for key, action in shortcuts:
            row = ttk.Frame(shortcuts_frame)
            row.pack(fill="x", pady=2, padx=8)
            ttk.Label(row, text=key, width=20, anchor="w", font=("Consolas", 10)).pack(side="left")
            ttk.Label(row, text=action, anchor="w").pack(side="left")

        ttk.Button(container, text="Back", command=self.on_back, width=14).pack(pady=(24, 0))

    def _add_checkbox(self, parent: tk.Widget, label: str, variable: tk.BooleanVar, key: str) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=6)
        ttk.Label(row, text=label, width=20, anchor="w").pack(side="left")
        ttk.Checkbutton(
            row, variable=variable, command=lambda: self.on_change(key, variable.get())
        ).pack(side="left")
