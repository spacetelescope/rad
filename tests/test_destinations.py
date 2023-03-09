import re
from sys import version_info

import pytest

if version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources

import rad.archive._destinations as destinations
from rad import resources

NUM_DESTINATIONS = 163
DESTINATIONS = [
    "ScienceCommon",
    "ScienceRefData",
]
_DESTINATION_REGEX = re.compile(f"[{', '.join(DESTINATIONS)}]")


@pytest.mark.parametrize("schema_path", (importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
def test_load_schema(schema_path):
    """Test loading all the schemas and making they are flattened correctly."""
    data = destinations._load_schema(schema_path)
    assert isinstance(data, dict)
    for key, value in data.items():
        assert isinstance(key, tuple)
        assert not isinstance(value, dict)
        assert not isinstance(value, list)


def test_search_keys():
    """Test that we can search multiple keys from a flat schema dictionary."""

    schema = {
        ("a", "b", "c"): 1,
        ("a", "b", "d"): 2,
        ("a", "e", "f"): 3,
        ("g", "h", "i"): 4,
    }

    keys = ["a", "b"]
    result = destinations._search_keys(schema, keys)

    assert result == {("a", "b", "c"): 1, ("a", "b", "d"): 2}


def test_destinations():
    """Test that we can get correct destinations from the schemas."""
    result = destinations.destinations()

    assert isinstance(result, list)
    for destination in result:
        assert isinstance(destination, str)
        assert _DESTINATION_REGEX.match(destination)

    assert len(result) == len(set(result)) == NUM_DESTINATIONS

    # Re-run the function to make sure the result doesn't change
    # It was because the original generator was exhausted, now the generator is fixed
    assert result == destinations.destinations()
