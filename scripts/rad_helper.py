from __future__ import annotations

from pathlib import Path

REPO_DIR = Path(__file__).parent.parent

if __name__ == "__main__":
    from helper import RadApp

    app = RadApp(REPO_DIR)
    app.run()
