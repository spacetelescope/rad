#!/usr/bin/env python3
"""
Insert the next release's changelog header.  Prints the version, which
our GitHub Actions workflow uses to generate a commit message.
"""
import re
from pathlib import Path

RELEASED_VERSION_RE = re.compile(r"\A(?P<major>[0-9]+)\.(?P<minor>[0-9])+\.[0-9]+ \([0-9]{4}-[0-9]{2}-[0-9]{2}\)$", re.MULTILINE)


def main():
    changelog_path = Path(__file__).absolute().parent.parent / "CHANGES.rst"
    content = changelog_path.read_text()

    match = RELEASED_VERSION_RE.match(content)
    if not match:
        raise RuntimeError("cannot determine latest released version")

    new_major = int(match.group("major"))
    new_minor = int(match.group("minor")) + 1
    version = f"{new_major}.{new_minor}.0"

    with changelog_path.open("w") as f:
        header = f"{version} (unreleased)"
        f.write(header + "\n")
        f.write("=" * len(header) + "\n\n")
        f.write(content)

    print(version, end=None)


if __name__ == "__main__":
    main()
