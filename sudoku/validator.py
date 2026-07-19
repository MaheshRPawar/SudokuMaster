"""Validation helpers shared by the solver, generator, and game logic."""

from __future__ import annotations

from typing import List

from sudoku.board import Board


def is_valid(board: Board, row: int, col: int, value: int) -> bool:
    """Check whether placing `value` at (row, col) breaks any Sudoku rule."""
    size = board.size

    for c in range(size):
        if c != col and board.grid[row][c] == value:
            return False

    for r in range(size):
        if r != row and board.grid[r][col] == value:
            return False

    box_index = board.box_index(row, col)
    for br, bc in board.box_cells(box_index):
        if (br, bc) != (row, col) and board.grid[br][bc] == value:
            return False

    return True


def is_board_valid(board: Board) -> bool:
    """Check that every filled cell on the board currently obeys the rules."""
    size = board.size
    for r in range(size):
        for c in range(size):
            value = board.grid[r][c]
            if value == 0:
                continue
            board.grid[r][c] = 0
            valid = is_valid(board, r, c, value)
            board.grid[r][c] = value
            if not valid:
                return False
    return True


def is_solved(board: Board) -> bool:
    """A board is solved when it is completely filled and internally valid."""
    return board.is_full() and is_board_valid(board)


def find_conflicts(board: Board, row: int, col: int) -> List[tuple[int, int]]:
    """Return coordinates of cells that conflict with the value at (row, col)."""
    value = board.grid[row][col]
    if value == 0:
        return []

    size = board.size
    conflicts = []

    for c in range(size):
        if c != col and board.grid[row][c] == value:
            conflicts.append((row, c))

    for r in range(size):
        if r != row and board.grid[r][col] == value:
            conflicts.append((r, col))

    box_index = board.box_index(row, col)
    for br, bc in board.box_cells(box_index):
        if (br, bc) != (row, col) and board.grid[br][bc] == value and (br, bc) not in conflicts:
            conflicts.append((br, bc))

    return conflicts
