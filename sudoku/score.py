"""Scoring and star-rating logic for a completed SudokuMaster game."""

from __future__ import annotations

DIFFICULTY_MULTIPLIER = {
    "Easy": 1.0,
    "Medium": 1.5,
    "Hard": 2.0,
    "Expert": 3.0,
}

SIZE_MULTIPLIER = {4: 0.7, 6: 1.0, 9: 1.5}

BASE_SCORE = 1000
MISTAKE_PENALTY = 40
HINT_PENALTY = 60


def calculate_score(
    size: int,
    difficulty: str,
    remaining_seconds: int,
    total_seconds: int,
    mistakes: int,
    hints_used: int,
) -> int:
    """Combine difficulty, board size, speed, mistakes, and hints into a score."""
    difficulty_factor = DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)
    size_factor = SIZE_MULTIPLIER.get(size, 1.0)

    time_ratio = remaining_seconds / total_seconds if total_seconds else 0
    speed_bonus = BASE_SCORE * time_ratio * 0.5

    raw_score = (BASE_SCORE + speed_bonus) * difficulty_factor * size_factor
    raw_score -= mistakes * MISTAKE_PENALTY
    raw_score -= hints_used * HINT_PENALTY

    return max(0, round(raw_score))


def calculate_stars(
    difficulty: str,
    remaining_seconds: int,
    total_seconds: int,
    mistakes: int,
    hints_used: int,
) -> int:
    """Return a 1-5 star rating for the completed game."""
    time_ratio = remaining_seconds / total_seconds if total_seconds else 0
    stars = 5

    if mistakes > 0:
        stars -= min(2, (mistakes + 1) // 2)
    if hints_used > 0:
        stars -= min(2, hints_used)
    if time_ratio < 0.25:
        stars -= 1

    if difficulty in ("Hard", "Expert") and stars < 5 and mistakes == 0 and hints_used == 0:
        stars = min(5, stars + 1)

    return max(1, min(5, stars))
