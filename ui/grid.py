"""Canvas-based Sudoku grid widget.

Handles drawing the board, mouse/keyboard selection, and all highlighting
(selected cell, row, column, box, and matching numbers). It never touches
game rules directly; it only reports selections and key presses to callbacks
supplied by the owning screen.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from assets.theme import THEMES
from sudoku.board import Board
from sudoku.validator import find_conflicts


class SudokuGrid(tk.Canvas):
    def __init__(
        self,
        parent: tk.Widget,
        board: Board,
        theme_name: str,
        on_select: Optional[Callable[[int, int], None]] = None,
        on_number_input: Optional[Callable[[int, int, int], None]] = None,
        highlight_enabled: bool = True,
        size_px: int = 520,
        **kwargs,
    ):
        super().__init__(parent, width=size_px, height=size_px, highlightthickness=0, **kwargs)
        self.board = board
        self.theme_name = theme_name
        self.on_select = on_select
        self.on_number_input = on_number_input
        self.highlight_enabled = highlight_enabled
        self.size_px = size_px
        self.cell_px = size_px / board.size

        self.selected: Optional[tuple[int, int]] = None
        self.cell_rects: dict[tuple[int, int], int] = {}
        self.cell_texts: dict[tuple[int, int], int] = {}
        self.error_cells: set[tuple[int, int]] = set()
        self.locked = False

        self.bind("<Button-1>", self._handle_click)
        self.bind("<Key>", self._handle_key)
        self.bind("<Up>", lambda e: self._move_selection(-1, 0))
        self.bind("<Down>", lambda e: self._move_selection(1, 0))
        self.bind("<Left>", lambda e: self._move_selection(0, -1))
        self.bind("<Right>", lambda e: self._move_selection(0, 1))
        self.bind("<BackSpace>", lambda e: self._clear_selected())
        self.bind("<Delete>", lambda e: self._clear_selected())
        self.focus_set()

        self.draw_board()

    def apply_theme(self, theme_name: str) -> None:
        self.theme_name = theme_name
        self.draw_board()

    def set_board(self, board: Board) -> None:
        self.board = board
        self.selected = None
        self.error_cells.clear()
        self.cell_px = self.size_px / board.size
        self.draw_board()

    def set_locked(self, locked: bool) -> None:
        self.locked = locked

    def colors(self) -> dict:
        return THEMES.get(self.theme_name, THEMES["Dark"])

    def draw_board(self) -> None:
        self.delete("all")
        colors = self.colors()
        self.configure(bg=colors["background"])
        size = self.board.size
        self.cell_rects.clear()
        self.cell_texts.clear()

        for row in range(size):
            for col in range(size):
                x1, y1 = col * self.cell_px, row * self.cell_px
                x2, y2 = x1 + self.cell_px, y1 + self.cell_px
                is_fixed = self.board.fixed[row][col]
                fill = colors["cell_fixed_bg"] if is_fixed else colors["cell_editable_bg"]
                rect_id = self.create_rectangle(x1, y1, x2, y2, fill=fill, outline=colors["grid_line"])
                self.cell_rects[(row, col)] = rect_id

                value = self.board.grid[row][col]
                text = str(value) if value != 0 else ""
                text_color = colors["text_primary"] if is_fixed else colors["accent"]
                font_weight = "bold" if is_fixed else "normal"
                text_id = self.create_text(
                    x1 + self.cell_px / 2,
                    y1 + self.cell_px / 2,
                    text=text,
                    fill=text_color,
                    font=("Segoe UI", int(self.cell_px * 0.42), font_weight),
                )
                self.cell_texts[(row, col)] = text_id

        self._draw_box_lines(colors)
        self._apply_highlights()

    def _draw_box_lines(self, colors: dict) -> None:
        size = self.board.size
        box_rows, box_cols = self.board.box_rows, self.board.box_cols
        for row in range(0, size + 1, box_rows):
            width = 3 if row % box_rows == 0 else 1
            y = row * self.cell_px
            self.create_line(0, y, self.size_px, y, fill=colors["box_line"], width=width)
        for col in range(0, size + 1, box_cols):
            width = 3 if col % box_cols == 0 else 1
            x = col * self.cell_px
            self.create_line(x, 0, x, self.size_px, fill=colors["box_line"], width=width)

    def _handle_click(self, event: tk.Event) -> None:
        if self.locked:
            return
        col = int(event.x // self.cell_px)
        row = int(event.y // self.cell_px)
        if 0 <= row < self.board.size and 0 <= col < self.board.size:
            self.select_cell(row, col)

    def select_cell(self, row: int, col: int) -> None:
        self.selected = (row, col)
        self._apply_highlights()
        if self.on_select:
            self.on_select(row, col)

    def _move_selection(self, d_row: int, d_col: int) -> None:
        if self.locked:
            return
        if self.selected is None:
            self.select_cell(0, 0)
            return
        row, col = self.selected
        size = self.board.size
        new_row = min(max(row + d_row, 0), size - 1)
        new_col = min(max(col + d_col, 0), size - 1)
        self.select_cell(new_row, new_col)

    def _handle_key(self, event: tk.Event) -> None:
        if self.locked or self.selected is None:
            return
        row, col = self.selected
        if self.board.fixed[row][col]:
            return
        if event.char and event.char.isdigit():
            value = int(event.char)
            if 1 <= value <= self.board.size:
                if self.on_number_input:
                    self.on_number_input(row, col, value)

    def _clear_selected(self) -> None:
        if self.locked or self.selected is None:
            return
        row, col = self.selected
        if self.on_number_input:
            self.on_number_input(row, col, 0)

    def place_number(self, row: int, col: int, value: int, is_error: bool) -> None:
        text_id = self.cell_texts.get((row, col))
        if text_id is None:
            return
        colors = self.colors()
        self.itemconfig(text_id, text=str(value) if value != 0 else "")
        if is_error:
            self.error_cells.add((row, col))
        else:
            self.error_cells.discard((row, col))
        self._apply_highlights()

    def _apply_highlights(self) -> None:
        colors = self.colors()
        size = self.board.size

        for (row, col), rect_id in self.cell_rects.items():
            is_fixed = self.board.fixed[row][col]
            base = colors["cell_fixed_bg"] if is_fixed else colors["cell_editable_bg"]
            self.itemconfig(rect_id, fill=base)
            text_id = self.cell_texts[(row, col)]
            default_color = colors["text_primary"] if is_fixed else colors["accent"]
            self.itemconfig(text_id, fill=default_color)

        for row, col in self.error_cells:
            rect_id = self.cell_rects.get((row, col))
            if rect_id:
                self.itemconfig(rect_id, fill=colors["cell_error_bg"])

        if not self.highlight_enabled or self.selected is None:
            return

        sel_row, sel_col = self.selected
        box_index = self.board.box_index(sel_row, sel_col)
        box_cells = set(self.board.box_cells(box_index))
        selected_value = self.board.grid[sel_row][sel_col]

        for row in range(size):
            for col in range(size):
                if (row, col) in self.error_cells:
                    continue
                rect_id = self.cell_rects[(row, col)]
                if row == sel_row and col == sel_col:
                    continue
                if row == sel_row or col == sel_col or (row, col) in box_cells:
                    self.itemconfig(rect_id, fill=colors["cell_peer_bg"])
                if selected_value != 0 and self.board.grid[row][col] == selected_value:
                    self.itemconfig(rect_id, fill=colors["cell_match_bg"])

        selected_rect = self.cell_rects[(sel_row, sel_col)]
        if (sel_row, sel_col) not in self.error_cells:
            self.itemconfig(selected_rect, fill=colors["cell_selected_bg"])

    def highlight_conflicts(self, row: int, col: int) -> list[tuple[int, int]]:
        return find_conflicts(self.board, row, col)

    def reveal_solution(self, solved_board: Board) -> None:
        self.board = solved_board
        self.draw_board()
