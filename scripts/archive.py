from __future__ import annotations

import pprint
from argparse import ArgumentParser
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import TYPE_CHECKING

from git import Remote, Repo

from rad._parser import diff, dump

if TYPE_CHECKING:
    from collections.abc import Generator

    from deepdiff import DeepDiff

_RAD_URLS = (
    "https://github.com/spacetelescope/rad",
    "https://github.com/spacetelescope/rad.git",
    "git@github.com:spacetelescope/rad.git",
)


def _repo(path: Path) -> tuple[Repo, Remote]:
    """
    Pull all the tags from the RAD Repository.
    """
    try:
        from git import Repo
    except ImportError as e:
        raise ImportError("GitPython is required to run this script. Please install it with `pip install GitPython`.") from e

    repo = Repo(path)

    for remote in repo.remotes:
        with suppress(AttributeError):
            url = remote.url
            if url in _RAD_URLS:
                remote.fetch(tags=True)
                return repo, remote

    raise ValueError(
        f"Unable to find the main RAD repository remote. Please add a remote with one of the following URLs: {_RAD_URLS}"
    )


@contextmanager
def _repo_branch(repo: Repo, hexsha: str) -> Generator[None, None, None]:
    """
    Get the latest commit hash for the specified branch from the remote.
    """
    if repo.index.diff(None):
        raise RuntimeError("Unstaged changes in the working directory, please commit or stash them before running this.")

    file_diffs = repo.index.diff("HEAD")
    changed_latest = []

    if file_diffs:
        for file_diff in file_diffs:
            if file_diff.a_path.startswith("latest/"):
                changed_latest.append(file_diff.a_path)

        # Only want to change the latest files during this context the other changes should be preserved
        # so we stash them separately
        if changed_latest:
            repo.git.stash("push", *changed_latest)

        # Now stash any other changes
        repo.git.stash("push")

    # Checkout checkout the latest files from hexshaw in the primary repo.
    repo.git.checkout(hexsha, "--", "latest")

    # Apply the stashed changes back to the working directory
    if file_diffs:
        repo.git.stash("apply")

    yield

    # Reset the repo to the last committed state
    repo.git.reset("--hard")

    # We had some staged changes so we need to restore those
    if file_diffs:
        # Drop the stash missing the latest changes as we will just pop the first stash
        if changed_latest:
            repo.git.stash("drop")

        # Now pop the stash with the latest changes
        repo.git.stash("pop")

        # Restage all the files that were staged before
        for file_diff in file_diffs:
            repo.git.add(file_diff.a_path)


def _diff_repo(
    repo: Repo,
    hexsha: str,
    base_dir: Path,
    super_schema: bool = True,
    archive_json: bool = True,
    archive_yaml: bool = True,
    archive_txt: bool = True,
) -> DeepDiff:
    """Get differences between the current staged files and those in the specified commit hash.

    Parameters
    ----------
    repo
        The git repository object to use for RAD.
    hexsha
        The commit hash to compare against.

    Returns
    -------
    DeepDiff
        The differences between the current staged files and those in the specified commit hash.
    """
    print("Generating archive files for the current staged state...")
    current_schemas = dump(
        base_dir,
        super_schema=super_schema,
        archive_json=archive_json,
        archive_yaml=archive_yaml,
        archive_txt=archive_txt,
        verbose=True,
    )["archive_schemas"]

    with _repo_branch(repo, hexsha):
        print("Generating archive files for the current staged state...")
        main_schemas = dump(
            base_dir, super_schema=False, archive_json=False, archive_txt=False, archive_yaml=False, verbose=True
        )["archive_schemas"]

    return diff(current_schemas, main_schemas)


def _argparser() -> ArgumentParser:
    """Create the argument parser for the archive script."""
    parser = ArgumentParser(
        "rad_archive",
        description="Dump the RAD archive schemas to a specified directory in JSON, YAML, and TXT formats.",
    )
    parser.add_argument(
        "--save_dir",
        "-s",
        default=None,
        type=Path,
        help="Directory to save the dumped archive files. Defaults to 'archive_dump' in the",
    )
    parser.add_argument(
        "--diff",
        "-d",
        default="main",
        type=str,
        help="Directory to diff the dumped archive files against. If not specified, no diff will be performed.",
    )
    parser.add_argument(
        "--no_super_schema",
        action="store_false",
        help="Do not save the super schemas.",
    )
    parser.add_argument(
        "--no_archive_json",
        action="store_false",
        help="Do not save the archive schemas in JSON format.",
    )
    parser.add_argument(
        "--no_archive_yaml",
        action="store_false",
        help="Do not save the archive schemas in YAML format.",
    )
    parser.add_argument(
        "--no_archive_txt",
        action="store_false",
        help="Do not save the archive entries in TXT format.",
    )

    return parser


if __name__ == "__main__":
    args = _argparser().parse_args()
    repo, remote = _repo(Path(__file__).parent.parent)

    save_dir = args.save_dir or Path.cwd() / "archive_dump"

    hexsha = remote.refs[args.diff].commit.hexsha

    differences = _diff_repo(
        repo, hexsha, save_dir, args.no_super_schema, args.no_archive_json, args.no_archive_yaml, args.no_archive_txt
    )

    print("-------------------- DIFF RESULTS ------------------")
    with (save_dir / "diff.txt").open("w") as f:
        if differences:
            pp = pprint.PrettyPrinter(stream=f)
            pp.pprint(differences)
            pp = pprint.PrettyPrinter()
            pp.pprint(differences)

        else:
            f.write("No differences found.")
            print("No differences found.")
