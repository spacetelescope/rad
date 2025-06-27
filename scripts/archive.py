from pathlib import Path

from rad import Reader

if __name__ == "__main__":
    Reader.from_rad().create_archive(Path(__file__).parent.parent / "archive.json")
