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

The yaml data is then flattened into a single level dictionary, so that we can
ignore some of the keyword fields in the schema, which we claim do not effect the
functionality of the schema for file validation. While doing this, we also remove
the ordering of lists, because right now the ordering of a list (aside from
the propertyOrder keyword, which is ignored) does not matter for the schema validation
purposes. This is again done to avoid false positives for changes.

Note that the filtering and comparison of the schemas may not capture things perfectly,
and so the exact mechanism for comparing schema version may change in the future.
The main goal of these tests is to flag potential changes to a schema which may
indicate that a version bump is needed. If necessary, there is a builtin mechanism
for x-failing given comparisons, so we can ignore potential false positives.
"""

from io import BytesIO
from pathlib import Path
from re import findall

import pytest
import yaml
from git import Repo
from semantic_version import Version

from .conftest import CURRENT_RESOURCES

# Using a python library load the actual RAD repository data into python
# object which can be interacted with.
REPO = Repo(Path(__file__).parent.parent)

# The oldest version of RAD that is under schema versioning
BASE_RELEASE = Version("0.23.1")

# The keywords in the schemas that we claim don't matter for schema versioning
IGNORED_KEYWORDS = (
    "archive_catalog",
    "sdf",
    "title",
    "description",
    "propertyOrder",
)


def flatten_dict(dict_, parent_key=None, filter_keys=None):
    """
    Flattens a the dictionary extracted from the yaml direct yaml load of the schema
        Flattens the dictionary into a single level dictionary with keys being
        tuples in order of the path to the value in the original dictionary.

    Note
    ----
    The filter_keys are there so that we can ignore the keywords that we claim
    don't matter for schema versioning. This is because these have no effect on
    the file validation. See IGNORED_KEYWORDS for the list of keywords that are
    ignored. This list is subject to change.

    Parameters
    ----------
    dict_ : dict
        The yaml dictionary to flatten
    parent_key : tuple
        The parent key to use for the flattened dictionary
    filter_keys : tuple
        The keys to filter out of the flattened dictionary

    Returns
    -------
    dict
        The flattened dictionary with keys being tuples in order of the path to the value
    """
    # Initialize the parent_key and filter_keys to empty tuples if they are None
    parent_key = () if parent_key is None else parent_key
    filter_keys = () if filter_keys is None else filter_keys

    def _flatten_dict_generator(dict_, parent_key=None, filter_keys=None):
        """
        Generator for a flattened dictionary
            This returns a generator that yields the flattened dictionary's key
            value pairs.

        Note
        ----
        This is based off the flatten_dict generator example presented by
            https://www.freecodecamp.org/news/how-to-flatten-a-dictionary-in-python-in-4-different-ways/

        Parameters
        ----------
        dict_ : dict
            The yaml dictionary to flatten
        parent_key : tuple
            The parent key to use for the flattened dictionary
        filter_keys : tuple

        Yields
        ------
        tuple
            The key value pairs of the flattened dictionary
        """
        # Initialize the parent_key and filter_keys to empty tuples if they are None
        parent_key = () if parent_key is None else parent_key
        filter_keys = () if filter_keys is None else filter_keys

        # Iterate over the outer most dictionary relative to the parent_key
        for key, value in dict_.items():
            # Extend the parent key with the current key
            new_key = (*parent_key, key) if parent_key else (key,)

            # If one of the keys is in the filter_keys, skip it
            if key in filter_keys:
                continue

            # Match the value type to determine how to handle it
            # yaml safe_load should return a dict with other dicts, lists, or
            # primitives
            match value:
                # Handle the case where the value is a dictionary
                # This is Just a recursive call to the generator
                case dict():
                    yield from _flatten_dict_generator(value, new_key, filter_keys)
                # Handle the case where the value is a list
                case list():
                    for val in value:
                        # Use same key "list" for all items in the list because
                        # for the RAD schemas list ordering is not important for
                        # schema operation outside of the propertyOrder, which is
                        # being ignored by the filter_keys
                        yield from _flatten_dict_generator({"list": val}, new_key, filter_keys)
                # Handle the case where the value is a primitive
                case _:
                    yield new_key, value

    # Expand the generator into a dictionary
    return dict(_flatten_dict_generator(dict_, parent_key, filter_keys))


# Get the current resources read through the conftest file and flatten them
FLAT_CURRENT_RESOURCES = {uri: flatten_dict(schema, filter_keys=IGNORED_KEYWORDS) for uri, schema in CURRENT_RESOURCES.items()}


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
    pattern = r"\d+\.\d+\.\d+"

    # Set so that duplicates are removed (these come from the 0.23.1.dev tags)
    versions = set()
    # Loop over all the tags in the repository
    for tag in REPO.tags:
        # Regex match the tag version to get the version number, there should
        # only be one match. Ideally this should fail
        matches = findall(pattern, tag.name)
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
        Determines if a file should be included in

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
            schemas[schema["id"]] = flatten_dict(schema, filter_keys=IGNORED_KEYWORDS)

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


@pytest.fixture(scope="module", params=VERSIONS)
def rad_version(request):
    """
    Fixture for the RAD version to test against
    """
    return request.param


@pytest.fixture(scope="module", params=(*VERSIONS, "HEAD"))
def current_version(request):
    """
    Fixture for the version of RAD to test against including the current state
    of the repository.
    """
    return request.param


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

    # There is one small case between 0.23.1 and 0.24.0 where the manifest changed
    # but the version number did not. This is not a vital issue.
    EXPECTED_FAILS = (
        ("0.23.1", "0.24.0", "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"),
        ("0.23.1", "HEAD", "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"),
    )

    def test_no_lost_uris(self, frozen_uri):
        """
        Test that all previously frozen schema uris are present in the current version

        Note
        ----
        If we decide to create an archive, we can simply include a check to a listing
        of those resources as part of the test.
        """
        assert frozen_uri in CURRENT_RESOURCES, f"Schema {frozen_uri} is not present in the current version"

    # Note it is probably sufficient to just check the current state of the repository
    # against the frozen versions, currently this checks everyversion against every
    # other version. Which is a bit overkill.
    def test_resource_changes(self, rad_version, current_version, frozen_uri):
        """
        Test that frozen schemas have not been changed between version including the
        current state of the repository
        """
        # Filter out the expected fails
        # Both both orders of versions need to be checked.
        if (rad_version, current_version, frozen_uri) in self.EXPECTED_FAILS or (
            current_version,
            rad_version,
            frozen_uri,
        ) in self.EXPECTED_FAILS:
            pytest.xfail(f"Schema {frozen_uri} is expected to have changed between version {rad_version} and {current_version}")

        # Get the resources for both the frozen and current versions
        frozen_resources = FROZEN_VERSIONS[rad_version]
        current_resources = FLAT_CURRENT_RESOURCES if current_version == "HEAD" else FROZEN_VERSIONS[current_version]

        # Only compare if both the frozen and current resources have the schema.
        # When a new schema is added, it will not be in the frozen resources
        # for previous versions, so we assume it works.
        # The test_no_lost_uris is to check the possibility of a schema being
        # removed from the current version.
        if frozen_uri in frozen_resources and frozen_uri in current_resources:
            # Get the flattened dictionary representation of both schemas
            frozen_resource = frozen_resources[frozen_uri]
            current_resource = current_resources[frozen_uri]

            # Check that the frozen resource is the same as the current resource
            assert frozen_resource == current_resource, (
                f"Resource {frozen_uri} has changed between versions {rad_version} and {current_version}"
            )
