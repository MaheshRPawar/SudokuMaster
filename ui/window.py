"""Main application window and screen controller for SudokuMaster.

This module owns the Tk root, switches between the home screen, the game
screen, and the settings screen, and coordinates the timer tick loop,
sound effects, save/load, and the leaderboard.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from assets.theme import THEMES
from sudoku import storage
from sudoku.game import Game, TIME_LIMITS_SECONDS
from sudoku.validator import find_conflicts
from ui.animation import flash_cell, pulse_text_color
from ui.controls import ControlPanel
from ui.dialogs import GameOverDialog, WinDialog, confirm_dialog
from ui.grid import SudokuGrid
from ui.home import HomeScreen
from ui.settings import SettingsScreen
from ui.sound import SoundManager

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SudokuMaster")
        self.geometry("980x680")
        self.minsize(860, 600)

        self._set_icon()

        self.settings = storage.load_settings()
        self.sound = SoundManager(enabled=self.settings["sound_enabled"])
        self.theme_name = self.settings["theme"]

        self.game: Game | None = None
        self.current_frame: ttk.Frame | None = None
        self._tick_job = None

        self.style = ttk.Style(self)
        self._apply_ttk_theme()

        self.configure(bg=THEMES[self.theme_name]["background"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.show_home()

    def _set_icon(self) -> None:
        icon_path = ASSETS_DIR / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

    def _apply_ttk_theme(self) -> None:
        colors = THEMES[self.theme_name]
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("TFrame", background=colors["background"])
        self.style.configure(
            "TLabel", background=colors["background"], foreground=colors["text_primary"]
        )
        self.style.configure(
            "TButton",
            background=colors["button_bg"],
            foreground=colors["button_fg"],
            padding=8,
        )
        self.style.map("TButton", background=[("active", colors["accent"])])
        self.style.configure("TCheckbutton", background=colors["background"], foreground=colors["text_primary"])
        self.style.configure("TLabelframe", background=colors["background"], foreground=colors["text_primary"])
        self.style.configure("TLabelframe.Label", background=colors["background"], foreground=colors["text_primary"])
        self.configure(bg=colors["background"])

    def _clear_frame(self) -> None:
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)
            self._tick_job = None
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_home(self) -> None:
        self._clear_frame()
        saved = storage.load_game() is not None
        frame = HomeScreen(
            self,
            theme_name=self.theme_name,
            default_size=9,
            default_difficulty="Medium",
            on_play=self._start_new_game,
            on_settings=self.show_settings,
            on_exit=self._on_close,
            has_saved_game=saved,
            on_resume=self._resume_saved_game,
        )
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

    def show_settings(self) -> None:
        self._clear_frame()
        frame = SettingsScreen(
            self,
            settings=self.settings,
            on_change=self._on_setting_change,
            on_back=self.show_home,
        )
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

    def _on_setting_change(self, key: str, value) -> None:
        self.settings[key] = value
        storage.save_settings(self.settings)

        if key == "sound_enabled":
            self.sound.set_enabled(value)
        elif key == "theme":
            self.theme_name = value
            self._apply_ttk_theme()
            if isinstance(self.current_frame, SettingsScreen):
                self.show_settings()

    def _start_new_game(self, size: int, difficulty: str) -> None:
        storage.clear_saved_game()
        self.game = Game(size, difficulty)
        self._show_game_screen()

    def _resume_saved_game(self) -> None:
        state = storage.load_game()
        if not state:
            self.show_home()
            return
        self.game = Game.from_state_dict(state)
        self._show_game_screen()
        self.game.resume_timer()
        self.control_panel.set_paused(False)

    def _show_game_screen(self) -> None:
        self._clear_frame()
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.current_frame = frame

        board_area = ttk.Frame(frame)
        board_area.pack(side="left", fill="both", expand=True)

        self.grid_widget = SudokuGrid(
            board_area,
            board=self.game.puzzle,
            theme_name=self.theme_name,
            on_select=self._on_cell_select,
            on_number_input=self._on_number_input,
            highlight_enabled=self.settings["grid_highlight"],
        )
        self.grid_widget.pack(expand=True)

        self.control_panel = ControlPanel(
            frame,
            theme_name=self.theme_name,
            board_size=self.game.size,
            on_number=self._on_pad_number,
            on_erase=self._on_erase,
            on_new_game=self._handle_new_game,
            on_restart=self._handle_restart,
            on_hint=self._handle_hint,
            on_check=self._handle_check,
            on_solve=self._handle_solve,
            on_pause_resume=self._handle_pause_resume,
            on_home=self._handle_home,
        )
        self.control_panel.pack(side="right", fill="y", padx=(20, 0))

        self._refresh_stats()
        self._tick_job = self.after(1000, self._tick)

    def _on_cell_select(self, row: int, col: int) -> None:
        pass

    def _on_pad_number(self, value: int) -> None:
        if self.grid_widget.selected is None:
            return
        row, col = self.grid_widget.selected
        self._on_number_input(row, col, value)

    def _on_erase(self) -> None:
        if self.grid_widget.selected is None:
            return
        row, col = self.grid_widget.selected
        self._on_number_input(row, col, 0)

    def _on_number_input(self, row: int, col: int, value: int) -> None:
        if self.game is None or self.game.game_over or self.game.paused:
            return

        if value == 0:
            self.game.clear_cell(row, col)
            self.grid_widget.place_number(row, col, 0, is_error=False)
            self.sound.play("click")
            return

        correct = self.game.place_value(row, col, value)
        self.grid_widget.place_number(row, col, value, is_error=not correct)
        self.sound.play("correct" if correct else "wrong")

        if not correct:
            rect_id = self.grid_widget.cell_rects[(row, col)]
            colors = THEMES[self.theme_name]
            flash_cell(self.grid_widget, rect_id, colors["danger"], colors["cell_error_bg"])

        self._refresh_stats()

        if self.game.game_over and self.game.won:
            self._handle_victory()

    def _refresh_stats(self) -> None:
        self.control_panel.update_timer(self.game.timer.format_remaining())
        self.control_panel.update_stats(self.game.mistakes, self.game.hints_used, self.game.max_hints)

    def _tick(self) -> None:
        if self.game is None:
            return
        expired = self.game.tick()
        self._refresh_stats()
        self._autosave()

        if expired:
            self.sound.play("lose")
            self._show_game_over_dialog()
            return

        self._tick_job = self.after(1000, self._tick)

    def _autosave(self) -> None:
        if self.game is not None and not self.game.game_over:
            storage.save_game(self.game.to_state_dict())

    def _handle_new_game(self) -> None:
        if confirm_dialog(self, self.theme_name, "Start a brand-new random puzzle?"):
            self.game.new_game()
            self.grid_widget.set_board(self.game.puzzle)
            self.control_panel.set_paused(False)
            self._refresh_stats()

    def _handle_restart(self) -> None:
        if confirm_dialog(self, self.theme_name, "Restart this puzzle? Your entries will be cleared."):
            self.game.restart_game()
            self.grid_widget.set_board(self.game.puzzle)
            self.control_panel.set_paused(False)
            self._refresh_stats()

    def _handle_hint(self) -> None:
        result = self.game.show_hint()
        if result is None:
            return
        row, col, value = result
        self.grid_widget.place_number(row, col, value, is_error=False)
        self.sound.play("click")
        self._refresh_stats()
        if self.game.game_over and self.game.won:
            self._handle_victory()

    def _handle_check(self) -> None:
        valid = self.game.check_solution()
        colors = THEMES[self.theme_name]
        flash_color = colors["success"] if valid else colors["danger"]
        for row in range(self.game.size):
            for col in range(self.game.size):
                if self.game.puzzle.grid[row][col] != 0:
                    conflicts = find_conflicts(self.game.puzzle, row, col)
                    if conflicts:
                        rect_id = self.grid_widget.cell_rects[(row, col)]
                        flash_cell(self.grid_widget, rect_id, colors["danger"], colors["cell_editable_bg"], times=2)
        self.sound.play("correct" if valid else "wrong")

    def _handle_solve(self) -> None:
        if confirm_dialog(self, self.theme_name, "Reveal the full solution? This will end the game."):
            self.game.solve_board()
            self.grid_widget.reveal_solution(self.game.puzzle)
            storage.clear_saved_game()
            storage.record_game_result(False, 0, self.game.timer.elapsed_seconds)

    def _handle_pause_resume(self) -> None:
        if self.game.paused:
            self.game.resume_timer()
            self.control_panel.set_paused(False)
            self.grid_widget.set_locked(False)
        else:
            self.game.pause_timer()
            self.control_panel.set_paused(True)
            self.grid_widget.set_locked(True)

    def _handle_home(self) -> None:
        if confirm_dialog(self, self.theme_name, "Return to the home screen? Progress is auto-saved."):
            self._autosave()
            self.show_home()

    def _handle_victory(self) -> None:
        storage.clear_saved_game()
        score = self.game.calculate_score()
        stars = self.game.calculate_stars()
        storage.record_game_result(True, score, self.game.timer.elapsed_seconds)
        self.sound.play("win")

        colors = THEMES[self.theme_name]
        for row in range(self.game.size):
            for col in range(self.game.size):
                rect_id = self.grid_widget.cell_rects[(row, col)]
                self.grid_widget.itemconfig(rect_id, fill=colors["success"])
        self.grid_widget.set_locked(True)

        text_ids = list(self.grid_widget.cell_texts.values())
        pulse_text_color(self.grid_widget, text_ids, [colors["text_primary"], colors["accent"]])

        minutes, seconds = divmod(self.game.timer.elapsed_seconds, 60)
        time_taken = f"{minutes:02d}:{seconds:02d}"

        WinDialog(
            self,
            self.theme_name,
            self.game.size,
            self.game.difficulty,
            time_taken,
            score,
            stars,
            self.game.hints_used,
            self.game.mistakes,
            on_play_again=self._restart_after_dialog,
            on_new_game=self._new_game_after_dialog,
            on_home=self.show_home,
            on_exit=self._on_close,
        )

    def _show_game_over_dialog(self) -> None:
        storage.clear_saved_game()
        storage.record_game_result(False, 0, self.game.timer.elapsed_seconds)
        self.grid_widget.set_locked(True)

        GameOverDialog(
            self,
            self.theme_name,
            on_retry=self._retry_after_dialog,
            on_play_again=self._new_game_after_dialog,
            on_home=self.show_home,
            on_exit=self._on_close,
        )

    def _retry_after_dialog(self) -> None:
        self.game.restart_game()
        self.grid_widget.set_locked(False)
        self.grid_widget.set_board(self.game.puzzle)
        self.control_panel.set_paused(False)
        self._refresh_stats()
        self._tick_job = self.after(1000, self._tick)

    def _restart_after_dialog(self) -> None:
        self._retry_after_dialog()

    def _new_game_after_dialog(self) -> None:
        self.game.new_game()
        self.grid_widget.set_locked(False)
        self.grid_widget.set_board(self.game.puzzle)
        self.control_panel.set_paused(False)
        self._refresh_stats()
        self._tick_job = self.after(1000, self._tick)

    def _on_close(self) -> None:
        self._autosave()
        self.destroy()
