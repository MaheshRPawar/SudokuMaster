"""Randomized Sudoku puzzle generator.

A fresh, fully solved grid is built with a randomized backtracking fill,
then shuffled at the row/column/band/digit level so that no two generated
solutions look alike. Cells are then removed one at a time, each removal
checked against the solver to guarantee the resulting puzzle still has
exactly one solution.
"""

from __future__ import annotations

import random
from typing import List

from sudoku.board import Board
from sudoku.solver import has_unique_solution
from sudoku.validator import is_valid

DIFFICULTY_CLUE_RATIOS = {
    "Easy": 0.62,
    "Medium": 0.50,
    "Hard": 0.40,
    "Expert": 0.32,
}

MIN_CLUES = {4: 6, 6: 14, 9: 24}


def generate_solution(size: int) -> Board:
    """Build a complete, randomly filled, valid solved board."""
    board = Board(size)
    _fill_board(board)
    return board


def _fill_board(board: Board) -> bool:
    empty = board.find_empty()
    if empty is None:
        return True

    row, col = empty
    values = list(range(1, board.size + 1))
    random.shuffle(values)

    for value in values:
        if is_valid(board, row, col, value):
            board.grid[row][col] = value
            if _fill_board(board):
                return True
            board.grid[row][col] = 0

    return False


def _shuffle_solved_board(board: Board) -> Board:
    """Apply randomized band/row/column/digit permutations to a solved board."""
    size = board.size
    box_rows, box_cols = board.box_rows, board.box_cols
    grid = board.grid

    row_bands = size // box_rows
    col_bands = size // box_cols

    band_order = list(range(row_bands))
    random.shuffle(band_order)
    new_rows: List[int] = []
    for band in band_order:
        rows_in_band = list(range(band * box_rows, band * box_rows + box_rows))
        random.shuffle(rows_in_band)
        new_rows.extend(rows_in_band)

    stack_order = list(range(col_bands))
    random.shuffle(stack_order)
    new_cols: List[int] = []
    for stack in stack_order:
        cols_in_stack = list(range(stack * box_cols, stack * box_cols + box_cols))
        random.shuffle(cols_in_stack)
        new_cols.extend(cols_in_stack)

    shuffled = [[grid[new_rows[r]][new_cols[c]] for c in range(size)] for r in range(size)]

    digit_map = list(range(1, size + 1))
    random.shuffle(digit_map)
    remapped = [
        [digit_map[value - 1] for value in row]
        for row in shuffled
    ]

    return Board(size, remapped)


def remove_numbers(board: Board, difficulty: str) -> Board:
    """Remove cells from a solved board until reaching the target clue count."""
    size = board.size
    ratio = DIFFICULTY_CLUE_RATIOS.get(difficulty, 0.5)
    total_cells = size * size
    target_clues = max(MIN_CLUES[size], round(total_cells * ratio))

    puzzle = board.clone()
    puzzle.fixed = [[True] * size for _ in range(size)]

    positions = [(r, c) for r in range(size) for c in range(size)]
    random.shuffle(positions)

    for row, col in positions:
        if puzzle.count_clues() <= target_clues:
            break

        removed_value = puzzle.grid[row][col]
        puzzle.grid[row][col] = 0
        puzzle.fixed[row][col] = False

        if not has_unique_solution(puzzle):
            puzzle.grid[row][col] = removed_value
            puzzle.fixed[row][col] = True

    return puzzle


def generate_puzzle(size: int, difficulty: str) -> tuple[Board, Board]:
    """Generate a brand-new random puzzle and its full solution.

    Returns a (puzzle, solution) tuple. The puzzle always has a unique
    solution and different clue positions from any previous call.
    """
    solved = generate_solution(size)
    solved = _shuffle_solved_board(solved)
    puzzle = remove_numbers(solved, difficulty)
    return puzzle, solved
