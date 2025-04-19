import importlib.resources as importlib_resources
from itertools import chain

import asdf
import pytest
import yaml

from rad import resources

MANIFEST_PATHS = tuple((importlib_resources.files(resources) / "manifests").glob("**/*.yaml"))
MANIFEST_URIS = tuple(yaml.safe_load(manifest_path.read_bytes())["id"] for manifest_path in MANIFEST_PATHS)
MANIFESTS = tuple(yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS)
MANIFEST_ENTRIES = tuple(chain(*[manifest["tags"] for manifest in MANIFESTS]))

LATEST_PATHS = tuple((importlib_resources.files(resources) / "latest").glob("**/*.yaml"))
LATEST_URIS = tuple(yaml.safe_load(latest_path.read_bytes())["id"] for latest_path in LATEST_PATHS)


@pytest.fixture(scope="session", params=MANIFEST_PATHS)
def manifest_path(request):
    return request.param


@pytest.fixture(scope="session", params=MANIFEST_ENTRIES)
def manifest_entry(request):
    return request.param


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=(importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
def schema_path(request):
    return request.param


@pytest.fixture(scope="session", params=LATEST_PATHS)
def latest_path(request):
    return request.param


@pytest.fixture(scope="session", params=LATEST_URIS)
def latest_uri(request):
    return request.param


@pytest.fixture(scope="session")
def latest_manifest_uri():
    latest_manifest_uris = tuple(uri for uri in LATEST_URIS if "manifests" in uri)
    assert len(latest_manifest_uris) == 1, "There should be exactly one latest manifest"
    return latest_manifest_uris[0]


@pytest.fixture(scope="session")
def latest_schemas():
    """
    Get the text of the latest schemas.
    """
    return {latest_uri: latest_path.read_text() for latest_uri, latest_path in zip(LATEST_URIS, LATEST_PATHS, strict=True)}


@pytest.fixture(scope="session")
def latest_schema_tags(latest_manifest_uri, latest_schemas):
    """
    Get the latest schema tags from the latest manifest.
    """
    tag_entries = yaml.safe_load(latest_schemas[latest_manifest_uri])["tags"]
    schema_tags = {entry["schema_uri"]: entry["tag_uri"] for entry in tag_entries}
    assert len(schema_tags) == len(tag_entries), "There should be no duplicate tags for a schema"
    return schema_tags
