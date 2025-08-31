"""
Helper functions to deduce the frozen URIs from the RAD repository's release history.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from re import findall
from tomllib import load

from git import Commit, Repo
from semantic_version import Version
from yaml import safe_load

_RAD_URLS = (
    "https://github.com/spacetelescope/rad.git",
    "git@github.com:spacetelescope/rad.git",
)

__all__ = ("frozen_uris",)


def frozen_uris(path: Path, base_release: Version | None = None) -> frozenset[str]:
    """
    Get a frozenset containing all the resource URIs that are frozen by a
    rad release starting from the base release.

    Parameters
    ----------
    path : Path
        The path to the RAD repository.

    base_release : Version | None, optional
        The base release version from which to start looking for frozen resources.
        If None (default), it will be read from the `pyproject.toml` file in the
        RAD repository.
    """
    if base_release is None:
        with (path / "pyproject.toml").open("rb") as f:
            base_release = Version(load(f)["tool"]["rad-versioning"]["base_release"])

    uris = set()
    for commit in _versions(base_release, _repo(path)):
        uris |= set(_frozen_resource_uris(commit))

    return frozenset(uris)


def _repo(path: Path) -> Repo:
    """
    Pull all the tags from the RAD Repository.
    """
    repo = Repo(path)

    for remote in repo.remotes:
        with suppress(AttributeError):
            url = remote.url
            if url in _RAD_URLS:
                remote.fetch(tags=True)
                return repo

    raise ValueError(
        f"Unable to find the main RAD repository remote. Please add a remote with one of the following URLs: {_RAD_URLS}"
    )


def _versions(base_release: Version, repo: Repo) -> Generator[Commit, None, None]:
    pattern = r"\d+\.\d+\.\d+$"

    versions: set[Version] = set()
    for tag in repo.tags:
        if v_match := findall(pattern, tag.name):
            version = Version(v_match[-1])

            if version >= base_release:
                versions.add(version)

    for version in sorted(versions):
        yield repo.commit(str(version))


def _frozen_resource_uris(release: Commit) -> Generator[str, None, None]:
    """
    Generate the URIs that are in the passed release commit of the RAD repository.

    Parameters
    ----------
    release : Commit
        The commit object from the RAD repository.

    Yields
    -------
    str
        The URIs of the frozen resources in the RAD repository.
    """

    def predicate(i, d):
        """
        Determines if a file should be included in
        """
        pattern = r".*\.yaml"
        if findall(pattern, i.path):
            return True
        return False

    for blob in release.tree.traverse(predicate=predicate):
        data = BytesIO(blob.data_stream.read()).read().decode("utf-8")
        if data.startswith("%YAML 1.1"):
            yield safe_load(data)["id"]
