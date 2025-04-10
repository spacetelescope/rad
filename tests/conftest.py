import importlib.resources as importlib_resources
from itertools import chain

import asdf
import pytest
import yaml

from rad import resources

MANIFEST_URIS = [
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0",
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.1.0",
]
MANIFESTS = [yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS]
MANIFEST_ENTRIES = []
for manifest in MANIFESTS:
    MANIFEST_ENTRIES.extend(manifest["tags"])


@pytest.fixture(scope="session", params=MANIFEST_ENTRIES)
def manifest_entry(request):
    return request.param


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(
    params=chain(
        (importlib_resources.files(resources) / "schemas").glob("**/*.yaml"),
        (importlib_resources.files(resources) / "latest").glob("**/*.yaml"),
    )
)
def schema_path(request):
    """
    Get the schema path for the test.
    """
    return request.param
