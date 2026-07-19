"""Home screen shown on launch: logo, board size / difficulty selection,
Play, Settings, and Exit.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from assets.theme import THEMES


class HomeScreen(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        theme_name: str,
        default_size: int,
        default_difficulty: str,
        on_play: Callable[[int, str], None],
        on_settings: Callable[[], None],
        on_exit: Callable[[], None],
        has_saved_game: bool,
        on_resume: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.theme_name = theme_name
        self.size_var = tk.IntVar(value=default_size)
        self.difficulty_var = tk.StringVar(value=default_difficulty)

        container = ttk.Frame(self)
        container.pack(expand=True)

        tk.Label(
            container,
            text="SUDOKU MASTER",
            font=("Consolas", 34, "bold"),
        ).pack(pady=(0, 4))
        ttk.Label(container, text="A modern, professional Sudoku experience", font=("Segoe UI", 12)).pack(
            pady=(0, 32)
        )

        selector_frame = ttk.Frame(container)
        selector_frame.pack(pady=8)

        ttk.Label(selector_frame, text="Board Size", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, padx=12, sticky="w"
        )
        size_menu = ttk.Combobox(
            selector_frame,
            textvariable=self.size_var,
            values=[4, 6, 9],
            state="readonly",
            width=8,
        )
        size_menu.grid(row=1, column=0, padx=12, pady=(4, 16))

        ttk.Label(selector_frame, text="Difficulty", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=1, padx=12, sticky="w"
        )
        difficulty_menu = ttk.Combobox(
            selector_frame,
            textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard", "Expert"],
            state="readonly",
            width=10,
        )
        difficulty_menu.grid(row=1, column=1, padx=12, pady=(4, 16))

        ttk.Button(
            container,
            text="Play",
            width=20,
            command=lambda: on_play(self.size_var.get(), self.difficulty_var.get()),
        ).pack(pady=6)

        if has_saved_game:
            ttk.Button(container, text="Resume Saved Game", width=20, command=on_resume).pack(pady=6)

        ttk.Button(container, text="Settings", width=20, command=on_settings).pack(pady=6)
        ttk.Button(container, text="Exit", width=20, command=on_exit).pack(pady=6)
