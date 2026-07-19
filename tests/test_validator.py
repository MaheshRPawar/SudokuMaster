import unittest

from sudoku.board import Board
from sudoku.validator import find_conflicts, is_board_valid, is_solved, is_valid


class TestValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = [[0] * 9 for _ in range(9)]
        self.grid[0][0] = 5
        self.board = Board(9, self.grid)

    def test_is_valid_rejects_row_duplicate(self) -> None:
        self.assertFalse(is_valid(self.board, 0, 1, 5))

    def test_is_valid_rejects_column_duplicate(self) -> None:
        self.assertFalse(is_valid(self.board, 1, 0, 5))

    def test_is_valid_rejects_box_duplicate(self) -> None:
        self.assertFalse(is_valid(self.board, 1, 1, 5))

    def test_is_valid_accepts_legal_placement(self) -> None:
        self.assertTrue(is_valid(self.board, 4, 4, 5))

    def test_is_board_valid_true_for_empty_board(self) -> None:
        board = Board(9)
        self.assertTrue(is_board_valid(board))

    def test_is_board_valid_false_with_conflict(self) -> None:
        grid = [[0] * 4 for _ in range(4)]
        grid[0][0] = 1
        grid[0][1] = 1
        board = Board(4, grid)
        self.assertFalse(is_board_valid(board))

    def test_is_solved_false_when_incomplete(self) -> None:
        self.assertFalse(is_solved(self.board))

    def test_find_conflicts_reports_all_conflicting_cells(self) -> None:
        grid = [[0] * 4 for _ in range(4)]
        grid[0][0] = 2
        grid[0][1] = 2
        grid[1][0] = 2
        board = Board(4, grid)
        conflicts = find_conflicts(board, 0, 0)
        self.assertIn((0, 1), conflicts)
        self.assertIn((1, 0), conflicts)

    def test_find_conflicts_empty_for_empty_cell(self) -> None:
        board = Board(4)
        self.assertEqual(find_conflicts(board, 0, 0), [])


if __name__ == "__main__":
    unittest.main()
