"""Core game engine package for SudokuMaster.

This package is fully independent of the UI layer and can be imported
and tested on its own.
"""

from sudoku.board import Board
from sudoku.game import Game

__all__ = ["Board", "Game"]
