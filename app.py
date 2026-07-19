"""SudokuMaster entry point.

Run this file to launch the desktop application:

    python app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ui.window import SudokuApp


def main() -> None:
    app = SudokuApp()
    app.mainloop()


if __name__ == "__main__":
    main()
