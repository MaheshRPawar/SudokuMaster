"""Lightweight canvas animation helpers used for win/lose effects.

Every animation is implemented with `Canvas.after` scheduling so it never
blocks the Tkinter event loop.
"""

from __future__ import annotations

import random
import tkinter as tk
from typing import Callable, Optional


def pulse_text_color(
    canvas: tk.Canvas,
    item_ids: list[int],
    colors: list[str],
    steps: int = 6,
    delay_ms: int = 90,
    on_done: Optional[Callable[[], None]] = None,
) -> None:
    """Cycle the fill color of the given canvas items to create a pulse."""

    def _step(index: int) -> None:
        if index >= steps:
            if on_done:
                on_done()
            return
        color = colors[index % len(colors)]
        for item_id in item_ids:
            try:
                canvas.itemconfig(item_id, fill=color)
            except tk.TclError:
                return
        canvas.after(delay_ms, _step, index + 1)

    _step(0)


def flash_cell(canvas: tk.Canvas, rect_id: int, flash_color: str, base_color: str, times: int = 3) -> None:
    """Flash a cell rectangle between a highlight color and its base color."""

    def _step(count: int) -> None:
        if count <= 0:
            try:
                canvas.itemconfig(rect_id, fill=base_color)
            except tk.TclError:
                pass
            return
        try:
            current = canvas.itemcget(rect_id, "fill")
            next_color = flash_color if current != flash_color else base_color
            canvas.itemconfig(rect_id, fill=next_color)
        except tk.TclError:
            return
        canvas.after(150, _step, count - 1)

    _step(times * 2)


class ConfettiBurst:
    """A simple particle-based confetti animation drawn on a Canvas overlay."""

    COLORS = ["#4f8cff", "#4caf7d", "#e05564", "#f2c14e", "#a77dff", "#eef1f8"]

    def __init__(self, canvas: tk.Canvas, width: int, height: int, particle_count: int = 70):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles: list[dict] = []
        self._running = False

        for _ in range(particle_count):
            x = random.uniform(0, width)
            y = random.uniform(-height, 0)
            size = random.uniform(4, 9)
            color = random.choice(self.COLORS)
            item_id = canvas.create_rectangle(
                x, y, x + size, y + size, fill=color, outline=""
            )
            self.particles.append(
                {
                    "id": item_id,
                    "vy": random.uniform(2.5, 6.0),
                    "vx": random.uniform(-1.5, 1.5),
                    "spin": random.uniform(-4, 4),
                }
            )

    def start(self, duration_ms: int = 2600) -> None:
        self._running = True
        self._animate(duration_ms)

    def _animate(self, remaining_ms: int) -> None:
        if not self._running or remaining_ms <= 0:
            self.stop()
            return

        for particle in self.particles:
            try:
                self.canvas.move(particle["id"], particle["vx"], particle["vy"])
            except tk.TclError:
                self._running = False
                return

        self.canvas.after(30, self._animate, remaining_ms - 30)

    def stop(self) -> None:
        self._running = False
        for particle in self.particles:
            try:
                self.canvas.delete(particle["id"])
            except tk.TclError:
                pass
        self.particles.clear()


def fade_overlay(
    canvas: tk.Canvas,
    rect_id: int,
    target_alpha_steps: int = 8,
    delay_ms: int = 40,
    color: str = "#5a0f16",
) -> None:
    """Simulate a fade-in by stepping the stipple pattern of an overlay rectangle."""
    stipples = ["", "gray12", "gray25", "gray50", "gray50", "gray75", "gray75", "gray75"]

    def _step(index: int) -> None:
        if index >= len(stipples):
            return
        try:
            canvas.itemconfig(rect_id, fill=color, stipple=stipples[index])
        except tk.TclError:
            return
        canvas.after(delay_ms, _step, index + 1)

    _step(0)
