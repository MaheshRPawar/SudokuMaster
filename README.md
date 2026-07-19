# SudokuMaster

A polished, professional Sudoku desktop application built entirely in Python with Tkinter and ttk. Every puzzle is randomly generated, guaranteed to have exactly one solution, and never repeats the same clue layout twice.

## Overview

SudokuMaster is a modular, portfolio-ready desktop game supporting 4x4, 6x6, and 9x9 boards across four difficulty levels. It features a countdown timer, hint system, mistake tracking, score and star-rating calculation, local save/resume, a persistent leaderboard, sound effects, animated win/lose sequences, and four selectable themes — all without any external dependencies beyond the Python standard library.

## Features

- **Randomized generation** — a fresh solved grid is built, shuffled at the row/column/band/digit level, and dug out cell by cell with a uniqueness check after every removal, so no two games are ever alike.
- **Three board sizes** — 4x4, 6x6, and 9x9, each with correctly sized boxes and rules.
- **Four difficulty levels** — Easy, Medium, Hard, Expert — controlling clue count, time limit, and hint allowance.
- **Countdown timer** — per-size, per-difficulty time limits with pause/resume support and an automatic Game Over on expiry.
- **Full gameplay toolkit** — New Game, Restart, Play Again, Home, Pause/Resume, Hint, Solve, Check, mistake counter, keyboard and mouse input.
- **Rich highlighting** — selected cell, row, column, box, and matching-number highlighting, toggleable in Settings.
- **Hint system** — a limited number of one-cell reveals per difficulty (5/3/2/1).
- **Scoring and star rating** — computed from difficulty, board size, remaining time, mistakes, and hints used.
- **Win and Game Over animations** — a green board flash with a pulsing confetti burst on victory, a red overlay on timeout.
- **Local save and resume** — the in-progress game is auto-saved every tick and can be resumed on next launch.
- **Local leaderboard** — best score, fastest time, games played/won, win percentage, and best streak, stored on disk.
- **Themes** — Dark, Light, Blue, and Classic, switchable instantly without restarting.
- **Sound effects** — click, correct, wrong, win, and lose sounds, with a mute toggle.
- **Accessibility** — full keyboard navigation (arrow keys, number keys, backspace/delete), an adjustable font-size slider, and a high-contrast option.

## Folder Structure

```text
SudokuMaster/
├── assets/
│   ├── icon.ico
│   ├── theme.py
│   └── sounds/
│       ├── click.wav
│       ├── correct.wav
│       ├── wrong.wav
│       ├── win.wav
│       └── lose.wav
├── sudoku/
│   ├── __init__.py
│   ├── board.py
│   ├── generator.py
│   ├── solver.py
│   ├── validator.py
│   ├── game.py
│   ├── timer.py
│   ├── score.py
│   └── storage.py
├── ui/
│   ├── __init__.py
│   ├── window.py
│   ├── home.py
│   ├── grid.py
│   ├── controls.py
│   ├── dialogs.py
│   ├── animation.py
│   ├── settings.py
│   └── sound.py
├── tests/
│   ├── __init__.py
│   ├── test_solver.py
│   ├── test_generator.py
│   └── test_validator.py
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## Requirements

SudokuMaster runs entirely on the Python standard library (Tkinter, ttk, `wave`, `winsound`/`subprocess`, `json`). No third-party packages are needed at runtime; `Pillow` is listed only because it was used to generate the app icon during development.

- Python 3.12 or newer
- Tkinter (bundled with most Python installers; on some Linux distributions install it separately, e.g. `sudo apt install python3-tk`)

## Run Instructions

```bash
python app.py       # Windows
python3 app.py       # Linux / macOS
```

On launch you'll land on the home screen, where you can pick a board size and difficulty and press **Play**. If a previous session exists, a **Resume Saved Game** button appears as well.

## Controls

| Input | Action |
|---|---|
| Mouse click | Select a cell |
| Arrow keys | Move the selection |
| 1–9 (or 1–4 / 1–6 depending on board size) | Enter a number in the selected cell |
| Backspace / Delete | Clear the selected cell |
| Number pad buttons | Enter a number with the mouse |
| Hint button | Reveal one correct cell (limited per difficulty) |
| Check button | Flash any cells that currently conflict with the rules |
| Solve button | Reveal the full solution and end the game |
| Pause / Resume button | Freeze or resume the countdown timer |

## Board Sizes

| Size | Box Shape |
|---|---|
| 4x4 | 2x2 boxes |
| 6x6 | 2x3 boxes |
| 9x9 | 3x3 boxes |

## Difficulty Levels and Time Limits

| Board | Easy | Medium | Hard | Expert |
|---|---|---|---|---|
| 4x4 | 1 min | 2 min | 3 min | 5 min |
| 6x6 | 5 min | 8 min | 10 min | 12 min |
| 9x9 | 10 min | 15 min | 20 min | 30 min |

Hint allowance: Easy 5, Medium 3, Hard 2, Expert 1.

## Algorithms

- **Solved-grid construction** — randomized backtracking fill (each cell's candidate digits are shuffled before being tried), producing a different valid solved grid on every call.
- **Grid transformation** — band, row, column-within-band, and digit relabeling permutations are applied to the solved grid so that even the same underlying pattern never looks the same twice.
- **Cell removal with uniqueness guarantee** — cells are removed one at a time in random order; each removal is kept only if the resulting puzzle still has exactly one solution, verified with a solver call after every attempt.
- **Solving and uniqueness checking** — both use a bitmask-based backtracking search with a minimum-remaining-values (MRV) heuristic, which tracks used digits per row/column/box as integers and always branches on the most-constrained empty cell first. This keeps generation and solving fast even for sparse Expert-level 9x9 boards.

## Testing

Unit tests cover the generator, solver, and validator modules:

```bash
python -m unittest discover tests       # Windows
python3 -m unittest discover tests       # Linux / macOS
```

## Future Improvements

- Difficulty rating based on required solving techniques (naked singles, hidden pairs, X-Wing, etc.) rather than clue count alone.
- Daily challenge mode with a shared seed and global leaderboard.
- Undo/redo history for placed numbers.
- Pencil-mark (candidate note) support in each cell.
- Packaged executables (PyInstaller) for Windows, macOS, and Linux.

## Git Commands

```bash
git init
git add .
git commit -m "Initial commit: SudokuMaster"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## License

Released under the [MIT License](LICENSE).

## Author

SudokuMaster was built as a portfolio-ready software engineering project demonstrating modular architecture, algorithmic puzzle generation, and a complete desktop UI in pure Python.

## Contributing

Issues and pull requests are welcome. Please keep new code PEP-8 compliant, covered by unit tests where applicable, and consistent with the existing module boundaries between `sudoku/` (game engine) and `ui/` (presentation layer).

## Acknowledgements

Built with the Python standard library — Tkinter/ttk for the interface, `wave` for sound synthesis, and `json` for local persistence.

## GitHub Topics

`python` `tkinter` `sudoku` `desktop-app` `game-development` `puzzle-generator` `backtracking-algorithm` `gui` `portfolio-project`
