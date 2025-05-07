import importlib.resources as importlib_resources
from itertools import chain
from pathlib import Path
from re import compile, match

import asdf
import pytest
import yaml
from semantic_version import Version

from rad import resources

RAD_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/"

MANIFEST_URI_PREFIX = f"{RAD_URI_PREFIX}manifests/"
MANIFEST_PATHS = tuple((importlib_resources.files(resources) / "manifests").glob("**/*.yaml"))
MANIFEST_URIS = tuple(yaml.safe_load(manifest_path.read_bytes())["id"] for manifest_path in MANIFEST_PATHS)
MANIFESTS = tuple(yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS)
MANIFEST_ENTRIES = tuple(chain(*[manifest["tags"] for manifest in MANIFESTS]))

TAG_URI_PREFIX = f"{RAD_URI_PREFIX}tags/"

SCHEMA_URI_PREFIX = f"{RAD_URI_PREFIX}schemas/"
METASCHEMA_URI = f"{SCHEMA_URI_PREFIX}rad_schema-1.0.0"
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

LATEST_PATHS = tuple((Path(__file__).parent.parent.absolute() / "latest").glob("**/*.yaml"))
LATEST_URIS = tuple(yaml.safe_load(latest_path.read_bytes())["id"] for latest_path in LATEST_PATHS)


CURRENT_RESOURCES = {
    uri: yaml.safe_load(asdf.get_config().resource_manager[uri])
    for uri in sorted(SCHEMA_URIS + MANIFEST_URIS + (METASCHEMA_URI,))
}


def get_latest_uri(prefix):
    """
    Get the latest exposure type URI.
    """
    pattern = rf"{prefix}-\d+\.\d+\.\d+$"
    uris = []
    for uri in CURRENT_RESOURCES:
        if match(pattern, uri):
            uris.append(uri)

    assert len(uris) > 0, "There should be at least one exposure type URI"

    version = Version("0.0.0")
    uri = None
    latest_uri = None
    for uri in uris:
        if version < (new := Version(uri.split("-")[-1])):
            version = new
            latest_uri = uri
    return latest_uri


EXPOSURE_TYPE_ELEMENTS = tuple(
    CURRENT_RESOURCES[get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/exposure_type")]["enum"]
)
P_EXPTYPE_PATTERN = CURRENT_RESOURCES[
    get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type")
]["properties"]["exposure"]["properties"]["p_exptype"]["pattern"]
OPTICAL_ELEMENTS = tuple(
    CURRENT_RESOURCES[get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/wfi_optical_element")]["enum"]
)
PHOT_TABLE_KEY_PATTERN = next(
    iter(
        CURRENT_RESOURCES[get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/reference_files/wfi_img_photom")][
            "properties"
        ]["phot_table"]["patternProperties"]
    )
)


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


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session", params=EXPOSURE_TYPE_ELEMENTS)
def exposure_type(request):
    """
    Get the exposure type from the request.
    """
    return request.param


@pytest.fixture(scope="session")
def exposure_types():
    """
    Get the exposure types from the request.
    """
    return EXPOSURE_TYPE_ELEMENTS


@pytest.fixture(scope="session")
def p_exptype_pattern():
    """
    Get the pattern for the exposure type used by the reference files.
    """
    return compile(P_EXPTYPE_PATTERN)


@pytest.fixture(scope="session", params=P_EXPTYPE_PATTERN.split(")\\s*\\|\\s*)+$")[0].split("((")[-1].split("|"))
def p_exptype(request):
    """
    Get the exposure type from the request.
    """
    return request.param


@pytest.fixture(scope="session", params=OPTICAL_ELEMENTS)
def optical_element(request):
    """
    Get the optical element from the request.
    """
    return request.param


@pytest.fixture(scope="session")
def optical_elements():
    """
    Get the optical elements from the request.
    """
    return OPTICAL_ELEMENTS


@pytest.fixture(scope="session")
def phot_table_key_pattern():
    """
    Get the pattern for the photometry table key used by the reference files.
    """
    return compile(PHOT_TABLE_KEY_PATTERN)


@pytest.fixture(scope="session", params=PHOT_TABLE_KEY_PATTERN.split(")$")[0].split("(")[-1].split("|"))
def phot_table_key(request):
    """
    Get the photometry table key from the request.
    """
    return request.param
