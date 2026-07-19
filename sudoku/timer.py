"""Countdown timer used to drive the per-game time limit.

The timer is UI-agnostic: it tracks elapsed and remaining seconds and
exposes simple start/pause/resume/reset controls. The UI layer is
responsible for calling `tick()` on a schedule (e.g. once per second).
"""

from __future__ import annotations


class CountdownTimer:
    def __init__(self, total_seconds: int):
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.running = False
        self._expired = False

    def start_timer(self) -> None:
        self.running = True

    def pause_timer(self) -> None:
        self.running = False

    def resume_timer(self) -> None:
        if not self._expired:
            self.running = True

    def reset(self, total_seconds: int | None = None) -> None:
        if total_seconds is not None:
            self.total_seconds = total_seconds
        self.remaining_seconds = self.total_seconds
        self.running = False
        self._expired = False

    def tick(self) -> bool:
        """Advance the timer by one second. Returns True if time just expired."""
        if not self.running or self._expired:
            return False

        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            self.running = False
            self._expired = True
            return True
        return False

    @property
    def expired(self) -> bool:
        return self._expired

    @property
    def elapsed_seconds(self) -> int:
        return self.total_seconds - self.remaining_seconds

    def format_remaining(self) -> str:
        minutes, seconds = divmod(max(self.remaining_seconds, 0), 60)
        return f"{minutes:02d}:{seconds:02d}"
