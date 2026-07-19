"""Core game logic: state machine tying together the board, timer, hints,
mistakes, and scoring. The UI layer only calls into this class; it never
manipulates the board or timer directly.
"""

from __future__ import annotations

from typing import Optional

from sudoku.board import Board
from sudoku.generator import generate_puzzle
from sudoku.score import calculate_score, calculate_stars
from sudoku.solver import solved_copy
from sudoku.timer import CountdownTimer
from sudoku.validator import is_solved, is_valid

TIME_LIMITS_SECONDS = {
    4: {"Easy": 60, "Medium": 120, "Hard": 180, "Expert": 300},
    6: {"Easy": 300, "Medium": 480, "Hard": 600, "Expert": 720},
    9: {"Easy": 600, "Medium": 900, "Hard": 1200, "Expert": 1800},
}

MAX_HINTS = {"Easy": 5, "Medium": 3, "Hard": 2, "Expert": 1}


class Game:
    """Represents a single Sudoku session in progress."""

    def __init__(self, size: int, difficulty: str):
        self.size = size
        self.difficulty = difficulty
        self.puzzle: Optional[Board] = None
        self.solution: Optional[Board] = None
        self.timer = CountdownTimer(TIME_LIMITS_SECONDS[size][difficulty])
        self.mistakes = 0
        self.hints_used = 0
        self.max_hints = MAX_HINTS[difficulty]
        self.game_over = False
        self.won = False
        self.paused = False
        self.new_game()

    def new_game(self) -> None:
        """Generate a brand-new random puzzle and reset all game state."""
        self.puzzle, self.solution = generate_puzzle(self.size, self.difficulty)
        self.mistakes = 0
        self.hints_used = 0
        self.game_over = False
        self.won = False
        self.paused = False
        self.timer.reset(TIME_LIMITS_SECONDS[self.size][self.difficulty])
        self.timer.start_timer()

    def restart_game(self) -> None:
        """Restart with the same puzzle, clearing only user entries."""
        if self.puzzle is None:
            return
        self.puzzle.clear_user_entries()
        self.mistakes = 0
        self.hints_used = 0
        self.game_over = False
        self.won = False
        self.paused = False
        self.timer.reset(TIME_LIMITS_SECONDS[self.size][self.difficulty])
        self.timer.start_timer()

    def play_again(self) -> None:
        """Alias for generating a completely new puzzle."""
        self.new_game()

    def change_settings(self, size: int, difficulty: str) -> None:
        self.size = size
        self.difficulty = difficulty
        self.max_hints = MAX_HINTS[difficulty]
        self.new_game()

    def pause_timer(self) -> None:
        self.paused = True
        self.timer.pause_timer()

    def resume_timer(self) -> None:
        self.paused = False
        self.timer.resume_timer()

    def tick(self) -> bool:
        """Advance the game clock. Returns True if the game just timed out."""
        if self.paused or self.game_over:
            return False
        expired = self.timer.tick()
        if expired:
            self.game_over = True
            self.won = False
        return expired

    def place_value(self, row: int, col: int, value: int) -> bool:
        """Attempt to place a value. Returns True if it was a correct move."""
        if self.puzzle is None or self.game_over or self.puzzle.fixed[row][col]:
            return False

        correct = self.solution.grid[row][col] == value
        self.puzzle.set(row, col, value)

        if not correct:
            self.mistakes += 1
        elif is_solved(self.puzzle):
            self.game_over = True
            self.won = True
            self.timer.pause_timer()

        return correct

    def clear_cell(self, row: int, col: int) -> bool:
        if self.puzzle is None or self.puzzle.fixed[row][col]:
            return False
        self.puzzle.set(row, col, 0)
        return True

    def show_hint(self) -> Optional[tuple[int, int, int]]:
        """Reveal one correct value. Returns (row, col, value) or None."""
        if self.hints_used >= self.max_hints or self.puzzle is None:
            return None

        for r in range(self.size):
            for c in range(self.size):
                if self.puzzle.grid[r][c] == 0:
                    value = self.solution.grid[r][c]
                    self.puzzle.fixed[r][c] = True
                    self.puzzle.grid[r][c] = value
                    self.hints_used += 1
                    if is_solved(self.puzzle):
                        self.game_over = True
                        self.won = True
                        self.timer.pause_timer()
                    return r, c, value
        return None

    def check_solution(self) -> bool:
        """Check whether the current board state is fully correct so far."""
        if self.puzzle is None:
            return False
        for r in range(self.size):
            for c in range(self.size):
                value = self.puzzle.grid[r][c]
                if value != 0 and not is_valid(self.puzzle, r, c, value):
                    return False
        return True

    def solve_board(self) -> None:
        """Reveal the full solution and end the game (used by the Solve button)."""
        if self.puzzle is None:
            return
        self.puzzle.grid = [row[:] for row in self.solution.grid]
        self.puzzle.fixed = [[True] * self.size for _ in range(self.size)]
        self.game_over = True
        self.won = False
        self.timer.pause_timer()

    def calculate_score(self) -> int:
        return calculate_score(
            self.size,
            self.difficulty,
            self.timer.remaining_seconds,
            self.timer.total_seconds,
            self.mistakes,
            self.hints_used,
        )

    def calculate_stars(self) -> int:
        return calculate_stars(
            self.difficulty,
            self.timer.remaining_seconds,
            self.timer.total_seconds,
            self.mistakes,
            self.hints_used,
        )

    def to_state_dict(self) -> dict:
        """Serialize the full game state for saving to disk."""
        return {
            "size": self.size,
            "difficulty": self.difficulty,
            "puzzle": self.puzzle.to_string(),
            "fixed_mask": "".join(
                "1" if self.puzzle.fixed[r][c] else "0"
                for r in range(self.size)
                for c in range(self.size)
            ),
            "solution": self.solution.to_string(),
            "remaining_seconds": self.timer.remaining_seconds,
            "total_seconds": self.timer.total_seconds,
            "mistakes": self.mistakes,
            "hints_used": self.hints_used,
        }

    @classmethod
    def from_state_dict(cls, state: dict) -> "Game":
        """Rebuild a Game instance from a previously saved state dictionary."""
        game = cls.__new__(cls)
        game.size = state["size"]
        game.difficulty = state["difficulty"]
        game.puzzle = Board.from_string(game.size, state["puzzle"], state["fixed_mask"])
        game.solution = Board.from_string(game.size, state["solution"])
        game.timer = CountdownTimer(state["total_seconds"])
        game.timer.remaining_seconds = state["remaining_seconds"]
        game.mistakes = state["mistakes"]
        game.hints_used = state["hints_used"]
        game.max_hints = MAX_HINTS[game.difficulty]
        game.game_over = False
        game.won = False
        game.paused = True
        return game
