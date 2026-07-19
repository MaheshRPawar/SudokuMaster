import unittest

from sudoku.board import Board
from sudoku.solver import count_solutions, has_unique_solution, solve_board, solved_copy
from sudoku.validator import is_solved


class TestSolver(unittest.TestCase):
    def setUp(self) -> None:
        self.solved_9x9 = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]

    def test_solves_valid_puzzle_with_one_missing_cell(self) -> None:
        grid = [row[:] for row in self.solved_9x9]
        grid[0][0] = 0
        board = Board(9, grid)
        self.assertTrue(solve_board(board))
        self.assertTrue(is_solved(board))
        self.assertEqual(board.grid[0][0], 5)

    def test_solve_fails_on_unsolvable_board(self) -> None:
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        grid[0][1] = 5  # immediate contradiction
        board = Board(9, grid)
        self.assertFalse(solve_board(board))

    def test_solved_copy_does_not_mutate_original(self) -> None:
        grid = [row[:] for row in self.solved_9x9]
        grid[3][3] = 0
        board = Board(9, grid)
        result = solved_copy(board)
        self.assertIsNotNone(result)
        self.assertEqual(board.grid[3][3], 0)
        self.assertEqual(result.grid[3][3], 7)

    def test_count_solutions_on_fully_solved_board(self) -> None:
        board = Board(9, self.solved_9x9)
        self.assertEqual(count_solutions(board), 1)

    def test_has_unique_solution_detects_multiple_solutions(self) -> None:
        grid = [[0] * 4 for _ in range(4)]
        board = Board(4, grid)
        self.assertFalse(has_unique_solution(board))

    def test_has_unique_solution_true_for_well_constrained_puzzle(self) -> None:
        grid = [row[:] for row in self.solved_9x9]
        grid[8][8] = 0
        board = Board(9, grid)
        self.assertTrue(has_unique_solution(board))


if __name__ == "__main__":
    unittest.main()
