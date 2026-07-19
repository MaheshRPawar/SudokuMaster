"""Cross-platform sound effect playback for SudokuMaster.

Uses the standard-library `winsound` module on Windows and shells out to
whatever native player is available on Linux/macOS. Every call is wrapped
so a missing audio backend never crashes the game; it simply plays no sound.
"""

from __future__ import annotations

import os
import platform
import subprocess
import threading
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"

SOUND_FILES = {
    "click": ASSETS_DIR / "click.wav",
    "correct": ASSETS_DIR / "correct.wav",
    "wrong": ASSETS_DIR / "wrong.wav",
    "win": ASSETS_DIR / "win.wav",
    "lose": ASSETS_DIR / "lose.wav",
}


class SoundManager:
    """Plays short WAV sound effects without blocking the UI thread."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._system = platform.system()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        path = SOUND_FILES.get(name)
        if path is None or not path.exists():
            return
        threading.Thread(target=self._play_file, args=(str(path),), daemon=True).start()

    def _play_file(self, path: str) -> None:
        try:
            if self._system == "Windows":
                import winsound

                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif self._system == "Darwin":
                subprocess.run(["afplay", path], check=False, capture_output=True)
            else:
                player = self._linux_player()
                if player:
                    subprocess.run(player + [path], check=False, capture_output=True)
        except Exception:
            pass

    @staticmethod
    def _linux_player() -> list[str] | None:
        for candidate in (["paplay"], ["aplay"], ["ffplay", "-nodisp", "-autoexit"]):
            if SoundManager._executable_exists(candidate[0]):
                return candidate
        return None

    @staticmethod
    def _executable_exists(name: str) -> bool:
        for directory in os.environ.get("PATH", "").split(os.pathsep):
            if (Path(directory) / name).exists():
                return True
        return False
