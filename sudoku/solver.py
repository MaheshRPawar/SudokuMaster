"""Backtracking solver used both to solve puzzles and to verify uniqueness.

The heavy lifting is done with a bitmask + minimum-remaining-values (MRV)
backtracking core. Tracking used digits per row/column/box as bitmasks
turns legality checks into O(1) operations, and always branching on the
most-constrained empty cell first prunes the search tree dramatically
compared to naive left-to-right backtracking. This is what keeps puzzle
generation and uniqueness checking fast even for sparse 9x9 boards.
"""

from __future__ import annotations

from typing import Optional

from sudoku.board import Board


class _FastState:
    """Bitmask-based scratch state for fast solving and solution counting."""

    __slots__ = (
        "size", "box_rows", "box_cols", "grid", "row_masks", "col_masks", "box_masks", "empties", "contradiction",
    )

    def __init__(self, board: Board):
        self.size = board.size
        self.box_rows = board.box_rows
        self.box_cols = board.box_cols
        self.grid = [row[:] for row in board.grid]

        size = self.size
        self.row_masks = [0] * size
        self.col_masks = [0] * size
        self.box_masks = [0] * size
        self.empties = []
        self.contradiction = False

        boxes_per_row = size // self.box_cols
        for r in range(size):
            for c in range(size):
                value = self.grid[r][c]
                b = (r // self.box_rows) * boxes_per_row + (c // self.box_cols)
                if value == 0:
                    self.empties.append((r, c, b))
                else:
                    bit = 1 << value
                    if (self.row_masks[r] & bit) or (self.col_masks[c] & bit) or (self.box_masks[b] & bit):
                        # Two pre-filled cells already break a Sudoku rule; the
                        # board can never be completed, so flag it up front
                        # instead of letting backtracking discover it the hard way.
                        self.contradiction = True
                    self.row_masks[r] |= bit
                    self.col_masks[c] |= bit
                    self.box_masks[b] |= bit

    def candidates(self, row: int, col: int, box: int) -> int:
        used = self.row_masks[row] | self.col_masks[col] | self.box_masks[box]
        full_mask = (1 << (self.size + 1)) - 2  # bits 1..size set
        return full_mask & ~used

    def place(self, row: int, col: int, box: int, value: int) -> None:
        bit = 1 << value
        self.grid[row][col] = value
        self.row_masks[row] |= bit
        self.col_masks[col] |= bit
        self.box_masks[box] |= bit

    def remove(self, row: int, col: int, box: int, value: int) -> None:
        bit = ~(1 << value)
        self.grid[row][col] = 0
        self.row_masks[row] &= bit
        self.col_masks[col] &= bit
        self.box_masks[box] &= bit

    def to_board(self) -> Board:
        return Board(self.size, self.grid)


def _bit_values(mask: int, size: int):
    for value in range(1, size + 1):
        if mask & (1 << value):
            yield value


def _solve_recursive(state: _FastState, empties: list) -> bool:
    if not empties:
        return True

    best_index = -1
    best_mask = None
    best_count = 99

    for index, (row, col, box) in enumerate(empties):
        mask = state.candidates(row, col, box)
        count = bin(mask).count("1")
        if count == 0:
            return False
        if count < best_count:
            best_count, best_index, best_mask = count, index, mask
            if count == 1:
                break

    row, col, box = empties[best_index]
    remaining = empties[:best_index] + empties[best_index + 1:]

    for value in _bit_values(best_mask, state.size):
        state.place(row, col, box, value)
        if _solve_recursive(state, remaining):
            return True
        state.remove(row, col, box, value)

    return False


def solve_board(board: Board) -> bool:
    """Solve the board in place using MRV-guided backtracking."""
    state = _FastState(board)
    if state.contradiction:
        return False
    if _solve_recursive(state, state.empties):
        board.grid = state.grid
        return True
    return False


def solved_copy(board: Board) -> Optional[Board]:
    """Return a solved clone of the board without mutating the original."""
    clone = board.clone()
    if solve_board(clone):
        return clone
    return None


def _count_recursive(state: _FastState, empties: list, limit: int) -> int:
    if not empties:
        return 1

    best_index = -1
    best_mask = None
    best_count = 99

    for index, (row, col, box) in enumerate(empties):
        mask = state.candidates(row, col, box)
        count = bin(mask).count("1")
        if count == 0:
            return 0
        if count < best_count:
            best_count, best_index, best_mask = count, index, mask
            if count == 1:
                break

    row, col, box = empties[best_index]
    remaining = empties[:best_index] + empties[best_index + 1:]

    total = 0
    for value in _bit_values(best_mask, state.size):
        state.place(row, col, box, value)
        total += _count_recursive(state, remaining, limit)
        state.remove(row, col, box, value)
        if total >= limit:
            return total

    return total


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count solutions up to `limit`. Stops early once the limit is reached."""
    state = _FastState(board)
    if state.contradiction:
        return 0
    return _count_recursive(state, state.empties, limit)


def has_unique_solution(board: Board) -> bool:
    """A puzzle is well-formed only if it has exactly one solution."""
    return count_solutions(board, limit=2) == 1
