"""Modal dialog windows: victory screen, game over screen, and a generic
confirmation prompt used throughout the app.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from assets.theme import THEMES
from ui.animation import ConfettiBurst


class WinDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        theme_name: str,
        board_size: int,
        difficulty: str,
        time_taken: str,
        score: int,
        stars: int,
        hints_used: int,
        mistakes: int,
        on_play_again: Callable[[], None],
        on_new_game: Callable[[], None],
        on_home: Callable[[], None],
        on_exit: Callable[[], None],
    ):
        super().__init__(parent)
        self.title("Puzzle Completed!")
        self.resizable(False, False)
        self.grab_set()
        colors = THEMES.get(theme_name, THEMES["Dark"])
        self.configure(bg=colors["surface"])

        width, height = 460, 480
        self.geometry(f"{width}x{height}")

        canvas = tk.Canvas(self, width=width, height=140, bg=colors["surface"], highlightthickness=0)
        canvas.pack(fill="x")
        confetti = ConfettiBurst(canvas, width, 140)
        confetti.start(2600)

        tk.Label(
            self,
            text="Congratulations!",
            font=("Segoe UI", 22, "bold"),
            fg=colors["success"],
            bg=colors["surface"],
        ).pack(pady=(0, 4))
        tk.Label(
            self, text="Puzzle Completed!", font=("Segoe UI", 13), fg=colors["text_secondary"], bg=colors["surface"]
        ).pack(pady=(0, 16))

        stats_frame = tk.Frame(self, bg=colors["surface"])
        stats_frame.pack(pady=4)

        rows = [
            ("Board Size", f"{board_size}x{board_size}"),
            ("Difficulty", difficulty),
            ("Time Taken", time_taken),
            ("Score", str(score)),
            ("Hints Used", str(hints_used)),
            ("Mistakes", str(mistakes)),
        ]
        for label, value in rows:
            row = tk.Frame(stats_frame, bg=colors["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 11), fg=colors["text_secondary"], bg=colors["surface"], width=14, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 11, "bold"), fg=colors["text_primary"], bg=colors["surface"], anchor="w").pack(side="left")

        star_text = "★" * stars + "☆" * (5 - stars)
        tk.Label(self, text=star_text, font=("Segoe UI", 20), fg=colors["accent"], bg=colors["surface"]).pack(pady=14)

        button_frame = tk.Frame(self, bg=colors["surface"])
        button_frame.pack(pady=10)

        def make_handler(callback: Callable[[], None]) -> Callable[[], None]:
            def _handler() -> None:
                confetti.stop()
                self.destroy()
                callback()
            return _handler

        buttons = [
            ("Play Again", on_play_again),
            ("New Game", on_new_game),
            ("Home", on_home),
            ("Exit", on_exit),
        ]
        for index, (label, callback) in enumerate(buttons):
            ttk.Button(button_frame, text=label, command=make_handler(callback), width=12).grid(
                row=index // 2, column=index % 2, padx=6, pady=6
            )


class GameOverDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        theme_name: str,
        on_retry: Callable[[], None],
        on_play_again: Callable[[], None],
        on_home: Callable[[], None],
        on_exit: Callable[[], None],
    ):
        super().__init__(parent)
        self.title("Time's Up!")
        self.resizable(False, False)
        self.grab_set()
        colors = THEMES.get(theme_name, THEMES["Dark"])
        self.configure(bg=colors["surface"])
        self.geometry("380x260")

        tk.Label(
            self, text="Time's Up!", font=("Segoe UI", 22, "bold"), fg=colors["danger"], bg=colors["surface"]
        ).pack(pady=(30, 6))
        tk.Label(
            self,
            text="The countdown reached zero.",
            font=("Segoe UI", 12),
            fg=colors["text_secondary"],
            bg=colors["surface"],
        ).pack(pady=(0, 24))

        button_frame = tk.Frame(self, bg=colors["surface"])
        button_frame.pack()

        def make_handler(callback: Callable[[], None]) -> Callable[[], None]:
            def _handler() -> None:
                self.destroy()
                callback()
            return _handler

        buttons = [
            ("Retry", on_retry),
            ("Play Again", on_play_again),
            ("Home", on_home),
            ("Exit", on_exit),
        ]
        for index, (label, callback) in enumerate(buttons):
            ttk.Button(button_frame, text=label, command=make_handler(callback), width=12).grid(
                row=index // 2, column=index % 2, padx=6, pady=6
            )


def confirm_dialog(parent: tk.Tk, theme_name: str, message: str, title: str = "Confirm") -> bool:
    """Show a Yes/No confirmation dialog and return the user's choice."""
    colors = THEMES.get(theme_name, THEMES["Dark"])
    result = {"confirmed": False}

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.configure(bg=colors["surface"])
    dialog.geometry("340x160")

    tk.Label(
        dialog, text=message, font=("Segoe UI", 12), fg=colors["text_primary"], bg=colors["surface"],
        wraplength=300, justify="center",
    ).pack(pady=(30, 20), padx=16)

    button_frame = tk.Frame(dialog, bg=colors["surface"])
    button_frame.pack()

    def on_yes() -> None:
        result["confirmed"] = True
        dialog.destroy()

    def on_no() -> None:
        result["confirmed"] = False
        dialog.destroy()

    ttk.Button(button_frame, text="Yes", command=on_yes, width=10).pack(side="left", padx=8)
    ttk.Button(button_frame, text="No", command=on_no, width=10).pack(side="left", padx=8)

    dialog.wait_window()
    return result["confirmed"]
