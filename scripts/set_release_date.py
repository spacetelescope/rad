#!/usr/bin/env python3
"""
Set the (latest and unreleased) changelog header release date to today.
Prints the version, which our GitHub Actions workflow uses to
generate a commit message and release tag.
"""
import re
from datetime import date
from pathlib import Path

UNRELEASED_VERSION_RE = re.compile(r"\A(?P<version>[0-9]+\.[0-9]+\.[0-9]+) \(unreleased\)$", re.MULTILINE)


def main():
    changelog_path = Path(__file__).absolute().parent.parent / "CHANGES.rst"
    content = changelog_path.read_text()

    match = UNRELEASED_VERSION_RE.match(content)
    if not match:
        raise RuntimeError("cannot determine latest unreleased version")

    version = match.group("version")
    new_heading = f"{version} ({date.today().isoformat()})"
    new_content = UNRELEASED_VERSION_RE.sub(new_heading, content)

    with changelog_path.open("w") as f:
        f.write(new_content)

    print(version, end=None)


if __name__ == "__main__":
    main()
