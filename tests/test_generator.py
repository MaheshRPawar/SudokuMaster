import unittest

from sudoku.generator import generate_puzzle, generate_solution
from sudoku.solver import has_unique_solution
from sudoku.validator import is_solved


class TestGenerator(unittest.TestCase):
    def test_generate_solution_is_fully_solved(self) -> None:
        for size in (4, 6, 9):
            with self.subTest(size=size):
                board = generate_solution(size)
                self.assertTrue(is_solved(board))

    def test_generate_puzzle_has_unique_solution(self) -> None:
        for size in (4, 6, 9):
            with self.subTest(size=size):
                puzzle, solution = generate_puzzle(size, "Medium")
                self.assertTrue(has_unique_solution(puzzle))
                self.assertTrue(is_solved(solution))

    def test_generate_puzzle_matches_solution(self) -> None:
        puzzle, solution = generate_puzzle(9, "Easy")
        for row in range(9):
            for col in range(9):
                if puzzle.grid[row][col] != 0:
                    self.assertEqual(puzzle.grid[row][col], solution.grid[row][col])

    def test_different_puzzles_on_repeated_generation(self) -> None:
        puzzle_one, _ = generate_puzzle(9, "Easy")
        puzzle_two, _ = generate_puzzle(9, "Easy")
        self.assertNotEqual(puzzle_one.to_string(), puzzle_two.to_string())

    def test_harder_difficulty_has_fewer_clues(self) -> None:
        easy_puzzle, _ = generate_puzzle(9, "Easy")
        expert_puzzle, _ = generate_puzzle(9, "Expert")
        self.assertGreater(easy_puzzle.count_clues(), expert_puzzle.count_clues())


if __name__ == "__main__":
    unittest.main()
