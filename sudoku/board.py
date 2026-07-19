"""Board representation for SudokuMaster.

The Board class stores the puzzle grid, the fixed-clue mask, and provides
simple helpers for reading and writing cell values without touching the
original clues.
"""

from __future__ import annotations

import math
from typing import List, Optional


class Board:
    """A square Sudoku board of a given size (4, 6, or 9)."""

    def __init__(self, size: int, values: Optional[List[List[int]]] = None):
        if size not in (4, 6, 9):
            raise ValueError("Board size must be 4, 6, or 9")

        self.size = size
        self.box_rows, self.box_cols = self._box_dimensions(size)
        self.grid: List[List[int]] = (
            [row[:] for row in values] if values else [[0] * size for _ in range(size)]
        )
        self.fixed: List[List[bool]] = [
            [self.grid[r][c] != 0 for c in range(size)] for r in range(size)
        ]

    @staticmethod
    def _box_dimensions(size: int) -> tuple[int, int]:
        """Return (box_rows, box_cols) for the given board size."""
        if size == 4:
            return 2, 2
        if size == 6:
            return 2, 3
        return 3, 3

    def clone(self) -> "Board":
        """Return a deep copy of this board, preserving fixed cells."""
        new_board = Board(self.size, self.grid)
        new_board.fixed = [row[:] for row in self.fixed]
        return new_board

    def get(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def set(self, row: int, col: int, value: int) -> bool:
        """Set a cell value. Returns False if the cell is a fixed clue."""
        if self.fixed[row][col]:
            return False
        self.grid[row][col] = value
        return True

    def clear_user_entries(self) -> None:
        """Clear every non-fixed cell, keeping the original clues intact."""
        for r in range(self.size):
            for c in range(self.size):
                if not self.fixed[r][c]:
                    self.grid[r][c] = 0

    def is_full(self) -> bool:
        return all(self.grid[r][c] != 0 for r in range(self.size) for c in range(self.size))

    def find_empty(self) -> Optional[tuple[int, int]]:
        """Find the first empty cell, or None if the board is full."""
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    return r, c
        return None

    def box_index(self, row: int, col: int) -> int:
        """Return the index (0-based) of the box containing (row, col)."""
        boxes_per_row = self.size // self.box_cols
        return (row // self.box_rows) * boxes_per_row + (col // self.box_cols)

    def box_cells(self, box_index: int) -> List[tuple[int, int]]:
        """Return all (row, col) coordinates belonging to a given box."""
        boxes_per_row = self.size // self.box_cols
        box_row = box_index // boxes_per_row
        box_col = box_index % boxes_per_row
        start_row = box_row * self.box_rows
        start_col = box_col * self.box_cols
        cells = []
        for r in range(start_row, start_row + self.box_rows):
            for c in range(start_col, start_col + self.box_cols):
                cells.append((r, c))
        return cells

    def to_string(self) -> str:
        """Serialize the grid as a flat digit string, using '0' for blanks."""
        return "".join(str(self.grid[r][c]) for r in range(self.size) for c in range(self.size))

    @classmethod
    def from_string(cls, size: int, data: str, fixed_mask: Optional[str] = None) -> "Board":
        """Rebuild a board from a flat digit string and an optional fixed mask."""
        values = [[0] * size for _ in range(size)]
        for i, char in enumerate(data):
            r, c = divmod(i, size)
            values[r][c] = int(char)
        board = cls(size, values)
        if fixed_mask is not None:
            board.fixed = [
                [fixed_mask[r * size + c] == "1" for c in range(size)] for r in range(size)
            ]
        return board

    def count_filled(self) -> int:
        return sum(1 for r in range(self.size) for c in range(self.size) if self.grid[r][c] != 0)

    def count_clues(self) -> int:
        return sum(1 for r in range(self.size) for c in range(self.size) if self.fixed[r][c])
