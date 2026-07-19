"""Control panel shown beside the Sudoku grid: number pad, action buttons,
and live stats (timer, mistakes, hints remaining).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from assets.theme import THEMES


class ControlPanel(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        theme_name: str,
        board_size: int,
        on_number: Callable[[int], None],
        on_erase: Callable[[], None],
        on_new_game: Callable[[], None],
        on_restart: Callable[[], None],
        on_hint: Callable[[], None],
        on_check: Callable[[], None],
        on_solve: Callable[[], None],
        on_pause_resume: Callable[[], None],
        on_home: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.theme_name = theme_name
        self.board_size = board_size

        self.timer_var = tk.StringVar(value="00:00")
        self.mistakes_var = tk.StringVar(value="Mistakes: 0")
        self.hints_var = tk.StringVar(value="Hints: 0/0")
        self.pause_label_var = tk.StringVar(value="Pause")

        self._build_stats_row()
        self._build_number_pad(on_number, on_erase)
        self._build_action_buttons(
            on_new_game, on_restart, on_hint, on_check, on_solve, on_pause_resume, on_home
        )

    def _build_stats_row(self) -> None:
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(stats_frame, textvariable=self.timer_var, font=("Consolas", 20, "bold")).pack(
            side="left", padx=(0, 16)
        )
        ttk.Label(stats_frame, textvariable=self.mistakes_var, font=("Segoe UI", 12)).pack(
            side="left", padx=(0, 16)
        )
        ttk.Label(stats_frame, textvariable=self.hints_var, font=("Segoe UI", 12)).pack(side="left")

    def _build_number_pad(self, on_number: Callable[[int], None], on_erase: Callable[[], None]) -> None:
        pad_frame = ttk.Frame(self)
        pad_frame.pack(fill="x", pady=(0, 12))

        columns = 5 if self.board_size == 9 else self.board_size
        for value in range(1, self.board_size + 1):
            row, col = divmod(value - 1, columns)
            btn = ttk.Button(pad_frame, text=str(value), width=4, command=lambda v=value: on_number(v))
            btn.grid(row=row, column=col, padx=3, pady=3)

        erase_row = (self.board_size - 1) // columns + 1
        erase_btn = ttk.Button(pad_frame, text="Erase", width=8, command=on_erase)
        erase_btn.grid(row=erase_row, column=0, columnspan=min(columns, 3), padx=3, pady=(8, 3), sticky="w")

    def _build_action_buttons(
        self,
        on_new_game: Callable[[], None],
        on_restart: Callable[[], None],
        on_hint: Callable[[], None],
        on_check: Callable[[], None],
        on_solve: Callable[[], None],
        on_pause_resume: Callable[[], None],
        on_home: Callable[[], None],
    ) -> None:
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill="x")

        buttons = [
            ("New Game", on_new_game),
            ("Restart", on_restart),
            ("Hint", on_hint),
            ("Check", on_check),
            ("Solve", on_solve),
        ]

        for index, (label, command) in enumerate(buttons):
            row, col = divmod(index, 2)
            ttk.Button(actions_frame, text=label, command=command, width=12).grid(
                row=row, column=col, padx=4, pady=4, sticky="ew"
            )

        self.pause_button = ttk.Button(
            actions_frame, textvariable=self.pause_label_var, command=on_pause_resume, width=12
        )
        self.pause_button.grid(row=3, column=0, padx=4, pady=4, sticky="ew")

        ttk.Button(actions_frame, text="Home", command=on_home, width=12).grid(
            row=3, column=1, padx=4, pady=4, sticky="ew"
        )

        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)

    def update_timer(self, formatted_time: str, low_time: bool = False) -> None:
        self.timer_var.set(formatted_time)

    def update_stats(self, mistakes: int, hints_used: int, max_hints: int) -> None:
        self.mistakes_var.set(f"Mistakes: {mistakes}")
        self.hints_var.set(f"Hints: {hints_used}/{max_hints}")

    def set_paused(self, paused: bool) -> None:
        self.pause_label_var.set("Resume" if paused else "Pause")
