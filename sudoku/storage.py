"""Local persistence for save-game state, settings, and the leaderboard.

Everything is stored as plain JSON files inside the user's home directory.
No network access or external database is used.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

APP_DIR_NAME = ".sudokumaster"


def _app_dir() -> Path:
    home = Path.home()
    app_dir = home / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


SAVE_FILE = "save.json"
SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound_enabled": True,
    "animations_enabled": True,
    "theme": "Dark",
    "accent_color": "#4f8cff",
    "grid_highlight": True,
    "timer_enabled": True,
    "font_scale": 1.0,
    "high_contrast": False,
}

DEFAULT_LEADERBOARD = {
    "best_score": 0,
    "fastest_time_seconds": None,
    "games_played": 0,
    "games_won": 0,
    "best_streak": 0,
    "current_streak": 0,
}


def _read_json(filename: str, default: dict) -> dict:
    path = _app_dir() / filename
    if not path.exists():
        return dict(default)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        merged = dict(default)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(default)


def _write_json(filename: str, data: dict) -> None:
    path = _app_dir() / filename
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    os.replace(tmp_path, path)


def save_game(state: dict) -> None:
    """Persist the current game state so it can be resumed later."""
    _write_json(SAVE_FILE, state)


def load_game() -> Optional[dict]:
    """Load a previously saved game, or None if no save exists."""
    path = _app_dir() / SAVE_FILE
    if not path.exists():
        return None
    return _read_json(SAVE_FILE, {})


def clear_saved_game() -> None:
    path = _app_dir() / SAVE_FILE
    if path.exists():
        path.unlink()


def load_settings() -> dict:
    return _read_json(SETTINGS_FILE, DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    _write_json(SETTINGS_FILE, settings)


def load_leaderboard() -> dict:
    return _read_json(LEADERBOARD_FILE, DEFAULT_LEADERBOARD)


def save_leaderboard(data: dict) -> None:
    _write_json(LEADERBOARD_FILE, data)


def record_game_result(won: bool, score: int, time_taken_seconds: int) -> dict:
    """Update and persist the leaderboard after a game finishes."""
    board = load_leaderboard()
    board["games_played"] += 1

    if won:
        board["games_won"] += 1
        board["current_streak"] += 1
        board["best_streak"] = max(board["best_streak"], board["current_streak"])
        board["best_score"] = max(board["best_score"], score)
        fastest = board.get("fastest_time_seconds")
        if fastest is None or time_taken_seconds < fastest:
            board["fastest_time_seconds"] = time_taken_seconds
    else:
        board["current_streak"] = 0

    save_leaderboard(board)
    return board


def win_percentage(board: dict) -> float:
    played = board.get("games_played", 0)
    if not played:
        return 0.0
    return round(100 * board.get("games_won", 0) / played, 1)
