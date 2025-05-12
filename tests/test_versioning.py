"""
Verify RAD Schema Versioning

The theory of these tests is that once a schema is published as part of a RAD release,
it should not be changed in any way that would affect the validation of the schema.
Effectively, this means that once a release is made and schema change post that release,
needs a version bump.

The way this works is by searching through the local git history of the RAD repository
for all the schema files that are associated with each given release version. This
assumes that the RAD repository tagging scheme remainsthe same "0.23.1", "0.24.0" and
that the tags exactly correspond to the release versions of RAD on PyPi given that
tag. In theory, the setuptools_scm versioning should align the tags with the versions
of RAD on PyPi, but it is possible to move a tag in git after the fact. This should
not be done.

Note that this search is done only backwards until a given base release version,
which marks the start of schema versioning.

The comparison of two different versions of a schema is done using the data read
out of the schema file by the yaml library. This is done so that basic formatting,
comments, and other non-ordered things do not give a false positive for a change.
The yaml dictionary is then filtered to remove the keys that we clain don't matter
for the purposes of schema versioning. This dictionary is then what we use to check
for equality among the different versions of the schemas.

Note that the filtering and comparison of the schemas may not capture things perfectly,
and so the exact mechanism for comparing schema version may change in the future.
The main goal of these tests is to flag potential changes to a schema which may
indicate that a version bump is needed. If necessary, there is a builtin mechanism
for x-failing given comparisons, so we can ignore potential false positives.
"""

from collections.abc import Mapping
from contextlib import suppress
from io import BytesIO
from itertools import product
from pathlib import Path
from re import findall

import pytest
import yaml
from asdf.treeutil import walk_and_modify
from git import Repo
from semantic_version import Version

from .conftest import CURRENT_RESOURCES

# Using a python library load the actual RAD repository data into python
# object which can be interacted with.
REPO = Repo(Path(__file__).parent.parent)
RAD_URLS = (
    "https://github.com/spacetelescope/rad.git",
    "git@github.com:spacetelescope/rad.git",
)

# The oldest version of RAD that is under schema versioning
BASE_RELEASE = Version("0.25.0")

# Any expected versioning failures should be added here
EXPECTED_XFAILS = (
    # ("<version>", "<uri>"),
)

# The keywords in the schemas that we claim don't matter for schema versioning
IGNORED_KEYWORDS = (
    "archive_meta",
    "archive_catalog",
    "sdf",
    "title",
    "description",
    "propertyOrder",
)


def filter_ignored_keys(tree):
    """
    Filter out the ignored keys from the dictionary.

    Parameters
    ----------
    tree :
        The tree to filter

    Returns
    -------
    The filtered tree
    """

    def filter_ignored_keys(node):
        """
        Filter out the ignored keys from the dictionary.

        Parameters
        ----------
        node : Any
            node to filter

        Returns
        -------
        dict
            The filtered dictionary
        """
        if isinstance(node, Mapping):
            return {key: value for key, value in node.items() if key not in IGNORED_KEYWORDS}
        return node

    return walk_and_modify(tree, callback=filter_ignored_keys)


# Get the current resources read through the conftest file and flatten them
FILTERED_CURRENT_RESOURCES = {uri: filter_ignored_keys(schema) for uri, schema in CURRENT_RESOURCES.items()}


def update_tags():
    """
    Pull all the tags from the RAD Repository.
    """

    for remote in REPO.remotes:
        with suppress(AttributeError):
            url = remote.url
            if url in RAD_URLS:
                remote.fetch(tags=True)
                return

    raise ValueError(
        f"Unable to find the main RAD repository remote. Please add a remote with one of the following URLs: {RAD_URLS}"
    )


def get_versions():
    """
    Get all release versions for RAD that are under schema versioning.

    Note
    ----
    This bases things off the git repository itself for the RAD repository, meaning
    that this will only work when the tests are run with this file within the RAD
    repository.

    This assumes that the current tagging scheme for RAD (release versions: 0.23.1, 0.24.0, etc.)
    is followed, and that these tags exactly correspond to the released version of
    the RAD on PyPi.

    Returns
    -------
    tuple[str]
        A tuple of all the release versions for RAD that are under schema versioning
        in order of the version number.

    Returns
    -------
    tuple[str]
        A tuple of all the release versions for RAD that are under schema versioning
        in order of the version number.
    """
    # Note that the `$` means that it will only match if the version number is the
    # end of the string, this eliminates the possibility of detecting `dev` tags
    #     That is this will match `0.23.1` and `0.24.0` but not `0.25.0.dev`
    pattern = r"\d+\.\d+\.\d+$"

    # Set to avoid duplicates
    versions = set()
    # Loop over all the tags in the repository
    for tag in REPO.tags:
        # Regex match the tag version to get the version number, there should
        # only be one match. Ideally this should fail
        if matches := findall(pattern, tag.name):
            # This should never be the case based on the regex pattern but
            # its better to be safe than sorry.
            if len(matches) != 1:
                raise ValueError(f"Tag {tag.name} does not match the versioning scheme")

            # Turn the version into a semantic version object so that we can compare
            # it to the base (oldest) release version
            version = Version(matches[0])
            if version >= BASE_RELEASE:
                versions.add(version)

    # Sort the versions in order of the version number
    return tuple(str(v) for v in sorted(versions))


# Read out all the versioins for RAD.
VERSIONS = get_versions()


def get_frozen_schemas(version):
    """
    Returns the frozen schemas for a given version.

    Note
    ----
    By frozen schemas, we mean schemas that have appeared in some release version
    of RAD post BASE_RELEASE.

    Parameters
    ----------
    version : str
        The version of RAD to get the frozen schemas for.

    Returns
    -------
    dict
        URI -> flattened (filtered) schema dictionary representation.
    """
    # Get the commit for the version in question
    release = REPO.commit(version)

    def predicate(i, d):
        """
        Determines if a file should be included in the traversal output or not.

        Note
        ----
        GitPython can be used to traverse the files in a repository at any given
        commit. The "predicate" function is a function that is used to determine
        if the file should be included in the traversal or not. Note that this
        does not stop the traversal at a given level, but rather just filters
        the files that are returned by the traversal.

        Parameters
        ----------
        i : git.Blob
            The blob object for the file
        d : git.Tree
            The tree object for the directory

        Returns
        -------
        bool
            True if the file should be included in the traversal output, False otherwise
        """
        # Use regex to pull out the files that are yaml files
        pattern = r".*\.yaml"
        if findall(pattern, i.path):
            return True
        return False

    # Iterate over the traversal of the git repository at the given commit
    # searching for the yaml files
    schemas = {}
    for blob in release.tree.traverse(predicate=predicate):
        # Read the file blob directly from the git history corresponding to the
        # to the release version's commit
        data = BytesIO(blob.data_stream.read()).read().decode("utf-8")

        # Check that the file has the %YAML 1.1 header, which is required for
        # (and tested for) the RAD schemas.
        # This is a bit of a hack, to side step the fact that we have a bunch
        # of symlinks in the RAD repository that point to .yaml files. Git stores
        # the symlink data as text that is a relateive path to the file linked to
        # meaning that GitPython will simply return a string containing that relative
        # path. These do not have the %YAML 1.1 header, so we can use that to filter
        if data.startswith("%YAML 1.1"):
            schema = yaml.safe_load(data)
            schemas[schema["id"]] = filter_ignored_keys(schema)

    # Sort the schemas by their URI
    # This is done so that the tests are always in the same order
    return {uri: schemas[uri] for uri in sorted(schemas.keys())}


def get_frozen_schemas_for_all_versions():
    """
    Find all the frozen schema versions for all the releases post BASE_RELEASE.

    Returns
    -------
    dict
        Version -> URI -> flattened (filtered) schema dictionary representation
        dictionary representation of the frozen schemas.
    tuple
        A tuple of unique URIs from all frozen schemas.
    """
    schemas = {}
    uris = []
    for version in VERSIONS:
        version_schemas = get_frozen_schemas(version)
        schemas[version] = version_schemas
        for uri in version_schemas:
            if uri not in uris:
                uris.append(uri)

    return schemas, tuple(uris)


# Get all the frozen schema information and the set of frozen schema URIs
FROZEN_VERSIONS, FROZEN_URIS = get_frozen_schemas_for_all_versions()


@pytest.fixture(scope="module", params=FROZEN_URIS)
def frozen_uri(request):
    """
    Fixture to get a frozen schema URI to test against.
    """
    return request.param


class TestVersioning:
    """
    Test to verify that schema versioning has not been violated
    """

    def test_no_lost_uris(self, frozen_uri):
        """
        Test that all previously frozen schema uris are present in the current version

        Note
        ----
        If we decide to create an archive, we can simply include a check to a listing
        of those resources as part of the test.
        """
        assert frozen_uri in CURRENT_RESOURCES, f"Schema {frozen_uri} is not present in the current version"

    @pytest.mark.parametrize(
        ("rad_version", "frozen_uri"),
        [
            pytest.param(
                *item,
                marks=pytest.mark.xfail(
                    reason=f"Schema {item[1]} is expected to have changed between {item[0]} and the current changes"
                ),
            )
            if item in EXPECTED_XFAILS
            else item
            for item in product(VERSIONS, FROZEN_URIS)
        ],
    )
    def test_resource_changes(self, rad_version, frozen_uri):
        """
        Test that frozen schemas have not been changed between version including the
        current state of the repository
        """
        # Get the resources for both the frozen and current versions
        frozen_resources = FROZEN_VERSIONS[rad_version]

        # We need to check that the frozen_uri is in the set of frozen resources
        # under consideration. This is because a frozen_uri may be added in a subsequent
        # version, than the one we are checking against. This is not a problem, so the
        # test should simply pass by default.
        if frozen_uri in frozen_resources:
            # Get the flattened dictionary representation of both schemas
            frozen_resource = frozen_resources[frozen_uri]
            current_resource = FILTERED_CURRENT_RESOURCES[frozen_uri]

            # Check that the frozen resource is the same as the current resource
            assert frozen_resource == current_resource, (
                f"Resource {frozen_uri} has changed between versions {rad_version} and the current changes"
            )

    @pytest.mark.parametrize(("rad_version", "frozen_uri"), EXPECTED_XFAILS)
    def test_expected_xfails_relevance(self, rad_version, frozen_uri):
        """
        Test that the expected fails are relevant to the current version of RAD
        -> Smokes out when the EXPECTED_XFAILS are no longer relevant
        """
        assert rad_version in VERSIONS, f"Version {rad_version} is not a valid version of RAD"
        assert frozen_uri in FROZEN_URIS, f"URI {frozen_uri} is not a valid frozen URI"
