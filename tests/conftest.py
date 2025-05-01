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

SCHEMA_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/schemas/"
METASCHEMA_URI = "asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0"
SCHEMA_URIS = tuple(u for u in asdf.get_config().resource_manager if u.startswith(SCHEMA_URI_PREFIX) and u != METASCHEMA_URI)
TAGGED_SCHEMA_URIS = set(entry["schema_uri"] for entry in MANIFEST_ENTRIES)
UNTAGGED_URIS = tuple(uri for uri in SCHEMA_URIS if uri not in TAGGED_SCHEMA_URIS)

TAG_DEFS = tuple(tag_def for manifest in MANIFESTS for tag_def in manifest["tags"])
REF_FILE_TAG_DEFS = tuple(tag_def for tag_def in TAG_DEFS if "/reference_files" in tag_def["schema_uri"])
ALLOWED_SCHEMA_TAG_VALIDATORS = (
    "tag:stsci.edu:asdf/time/time-1.*",
    "tag:stsci.edu:asdf/core/ndarray-1.*",
    "tag:stsci.edu:asdf/unit/quantity-1.*",
    "tag:stsci.edu:asdf/unit/unit-1.*",
    "tag:astropy.org:astropy/units/unit-1.*",
    "tag:astropy.org:astropy/table/table-1.*",
    "tag:stsci.edu:gwcs/wcs-*",
)

LATEST_PATHS = tuple((importlib_resources.files(resources) / "latest").glob("**/*.yaml"))
LATEST_URIS = tuple(yaml.safe_load(latest_path.read_bytes())["id"] for latest_path in LATEST_PATHS)


CURRENT_RESOURCES = {
    uri: yaml.safe_load(asdf.get_config().resource_manager[uri])
    for uri in sorted(SCHEMA_URIS + MANIFEST_URIS + (METASCHEMA_URI,))
}


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


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema_uri(request):
    return request.param


@pytest.fixture(scope="session")
def schema_content(schema_uri):
    return asdf.get_config().resource_manager[schema_uri]


@pytest.fixture()
def schema(schema_uri):
    return CURRENT_RESOURCES[schema_uri]


@pytest.fixture(scope="session")
def valid_tag_uris():
    uris = {t["tag_uri"] for manifest in MANIFESTS for t in manifest["tags"]}
    uris.update(ALLOWED_SCHEMA_TAG_VALIDATORS)
    return uris


@pytest.fixture(scope="session", params=REF_FILE_TAG_DEFS)
def ref_file_schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param["schema_uri"]])


@pytest.fixture(scope="session", params=REF_FILE_TAG_DEFS)
def ref_file_uris(request):
    return request.param["tag_uri"], request.param["schema_uri"]


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
