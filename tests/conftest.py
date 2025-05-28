import importlib.resources as importlib_resources
from itertools import chain
from pathlib import Path
from re import compile, match
from types import MappingProxyType

import asdf
import pytest
import yaml
from semantic_version import Version

from rad import resources


@pytest.fixture(scope="session", params=(importlib_resources.files(resources) / "manifests").glob("**/*.yaml"))
def manifest_path(request):
    """
    Get the paths to the manifest files directly from python package, rather than ASDF
    """
    return request.param


@pytest.fixture(scope="session", params=(importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
def schema_path(request):
    """
    Get the paths to the schema files directly from python package, rather than ASDF
    """
    return request.param


# Defined directly so that the value can be reused to find the URIs from the ASDF resource manager
# outside of a pytest fixture
_RAD_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/"
_MANIFEST_URI_PREFIX = f"{_RAD_URI_PREFIX}manifests/"
_SCHEMA_URI_PREFIX = f"{_RAD_URI_PREFIX}schemas/"
_METASCHEMA_URI = f"{_SCHEMA_URI_PREFIX}rad_schema-1.0.0"


@pytest.fixture(scope="session")
def rad_uri_prefix():
    """
    Get the RAD URI prefix.
    """
    return _RAD_URI_PREFIX


@pytest.fixture(scope="session")
def manifest_uri_prefix():
    """
    Get the manifest URI prefix.
    """
    return _MANIFEST_URI_PREFIX


@pytest.fixture(scope="session")
def schema_uri_prefix():
    return _SCHEMA_URI_PREFIX


@pytest.fixture(scope="session")
def metaschema_uri():
    """
    Get the metaschema URI.
    """
    return _METASCHEMA_URI


@pytest.fixture(scope="session")
def tag_uri_prefix(rad_uri_prefix):
    return f"{rad_uri_prefix}tags/"


# Get all the schema URIs from the ASDF resource manager cached to the current session
# to avoid loading them multiple times
_MANIFEST_URIS = tuple(uri for uri in asdf.get_config().resource_manager if uri.startswith(_MANIFEST_URI_PREFIX))
_SCHEMA_URIS = tuple(u for u in asdf.get_config().resource_manager if u.startswith(_SCHEMA_URI_PREFIX) and u != _METASCHEMA_URI)
_URIS = _SCHEMA_URIS + _MANIFEST_URIS + (_METASCHEMA_URI,)


@pytest.fixture(scope="session")
def manifest_uris():
    """
    Get the manifest URIs.
    """
    return _MANIFEST_URIS


@pytest.fixture(scope="session", params=_MANIFEST_URIS)
def manifest_uri(request):
    """
    Get the URIs of the manifest files from the ASDF resource manager.
    """
    return request.param


@pytest.fixture(scope="session")
def schema_uris():
    """
    Get all the URIs of RAD from the ASDF resource manager.
    """
    return _SCHEMA_URIS


@pytest.fixture(scope="session", params=_SCHEMA_URIS)
def schema_uri(request):
    return request.param


@pytest.fixture(scope="session")
def uris():
    """
    Get all the URIs of RAD from the ASDF resource manager.
    """
    return _URIS


@pytest.fixture(scope="session", params=_URIS)
def uri(request):
    """
    Get the URIs of the manifest files from the ASDF resource manager.
    """
    return request.param


@pytest.fixture(scope="session", params=tuple(uri for uri in _SCHEMA_URIS if "/reference_files" in uri))
def ref_file_uri(request):
    """
    Get the reference file schema URI from the request.
    """
    return request.param


# load all the schemas from the ASDF resource manager
_CURRENT_CONTENT = MappingProxyType({uri: asdf.get_config().resource_manager[uri] for uri in _URIS})
_CURRENT_RESOURCES = MappingProxyType({uri: yaml.safe_load(content) for uri, content in _CURRENT_CONTENT.items()})
_MANIFEST_ENTRIES = tuple(chain(*[_CURRENT_RESOURCES[uri]["tags"] for uri in _MANIFEST_URIS]))


@pytest.fixture(scope="session")
def current_content(uri):
    """
    Get the current content from the ASDF resource manager.
    """
    return _CURRENT_CONTENT[uri]


@pytest.fixture(scope="session")
def current_resources():
    """
    Get the current resources from the ASDF resource manager.
    """
    return _CURRENT_RESOURCES


@pytest.fixture(scope="session")
def manifest(manifest_uri, current_resources):
    """
    Get the manifests for the given uris.
    """
    return current_resources[manifest_uri]


@pytest.fixture(scope="session", params=_MANIFEST_ENTRIES)
def manifest_entry(request):
    """
    Get the manifest entry for the given request.
    """
    return request.param


@pytest.fixture(scope="session")
def manifest_by_schema(manifest_uris, current_resources):
    """
    Get the text of the manifests.
    """
    return MappingProxyType(
        {
            uri: MappingProxyType({entry["schema_uri"]: entry["tag_uri"] for entry in current_resources[uri]["tags"]})
            for uri in manifest_uris
        }
    )


@pytest.fixture(scope="session")
def manifest_by_tag(manifest_by_schema):
    """
    Get the text of the manifests.
    """
    return MappingProxyType(
        {uri: MappingProxyType({value: key for key, value in entry.items()}) for uri, entry in manifest_by_schema.items()}
    )


@pytest.fixture(scope="session")
def schema_tag_map(manifest_by_schema):
    """
    Get the schema tag map.
    """
    return MappingProxyType(
        {schema_uri: tag_uri for schema_tag_map in manifest_by_schema.values() for schema_uri, tag_uri in schema_tag_map.items()}
    )


@pytest.fixture(scope="session")
def schema(schema_uri, current_resources):
    """
    Return the yaml loaded schema for the given schema URI.
    """
    return current_resources[schema_uri]


@pytest.fixture(scope="session")
def ref_file_schema(ref_file_uri, current_resources):
    """
    Get the reference file tag URI from the request.
    """
    return current_resources[ref_file_uri]


@pytest.fixture(scope="session")
def manifest_entries():
    """
    Get the manifest entries.
    """
    return _MANIFEST_ENTRIES


@pytest.fixture(scope="session")
def tagged_schema_uris():
    """
    Get the tags from the manifest entries.
    """
    return frozenset(entry["schema_uri"] for entry in _MANIFEST_ENTRIES)


@pytest.fixture(scope="session")
def allowed_schema_tag_validators():
    """
    Get the allowed schema tag validators.
    """
    return frozenset(
        (
            "tag:stsci.edu:asdf/time/time-1.*",
            "tag:stsci.edu:asdf/core/ndarray-1.*",
            "tag:stsci.edu:asdf/unit/quantity-1.*",
            "tag:stsci.edu:asdf/unit/unit-1.*",
            "tag:astropy.org:astropy/units/unit-1.*",
            "tag:astropy.org:astropy/table/table-1.*",
            "tag:stsci.edu:gwcs/wcs-*",
        )
    )


@pytest.fixture(scope="session")
def valid_tag_uris(manifest_entries, allowed_schema_tag_validators):
    uris = set(entry["tag_uri"] for entry in manifest_entries)
    uris.update(allowed_schema_tag_validators)
    return frozenset(uris)


def _get_latest_uri(prefix):
    """
    Get the latest exposure type URI.
    """
    pattern = rf"{prefix}-\d+\.\d+\.\d+$"
    uris = []
    for uri in _CURRENT_RESOURCES:
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


_PHOT_TABLE_KEY_PATTERN = next(
    iter(
        _CURRENT_RESOURCES[_get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/reference_files/wfi_img_photom")][
            "properties"
        ]["phot_table"]["patternProperties"]
    )
)


@pytest.fixture(scope="session")
def phot_table_key_pattern():
    """
    Get the pattern for the photometry table key used by the reference files.
    """
    return compile(_PHOT_TABLE_KEY_PATTERN)


@pytest.fixture(scope="session", params=_PHOT_TABLE_KEY_PATTERN.split(")$")[0].split("(")[-1].split("|"))
def phot_table_key(request):
    """
    Get the photometry table key from the request.
    """
    return request.param


_OPTICAL_ELEMENTS = tuple(
    _CURRENT_RESOURCES[_get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/wfi_optical_element")]["enum"]
)


@pytest.fixture(scope="session", params=_OPTICAL_ELEMENTS)
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
    return _OPTICAL_ELEMENTS


_EXPOSURE_TYPE_ELEMENTS = tuple(
    _CURRENT_RESOURCES[_get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/exposure_type")]["enum"]
)


@pytest.fixture(scope="session", params=_EXPOSURE_TYPE_ELEMENTS)
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
    return _EXPOSURE_TYPE_ELEMENTS


_P_EXPTYPE_PATTERN = _CURRENT_RESOURCES[
    _get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type")
]["properties"]["exposure"]["properties"]["p_exptype"]["pattern"]


@pytest.fixture(scope="session")
def p_exptype_pattern():
    """
    Get the pattern for the exposure type used by the reference files.
    """
    return compile(_P_EXPTYPE_PATTERN)


@pytest.fixture(scope="session", params=_P_EXPTYPE_PATTERN.split(")\\s*\\|\\s*)+$")[0].split("((")[-1].split("|"))
def p_exptype(request):
    """
    Get the exposure type from the request.
    """
    return request.param


_LATEST_PATHS = tuple((Path(__file__).parent.parent.absolute() / "latest").glob("**/*.yaml"))
_LATEST_URIS = tuple(yaml.safe_load(latest_path.read_bytes())["id"] for latest_path in _LATEST_PATHS)


@pytest.fixture(scope="session")
def latest_paths():
    """
    Get the paths to the latest schemas.
    """
    return _LATEST_PATHS


@pytest.fixture(scope="session", params=_LATEST_PATHS)
def latest_path(request):
    """
    Get a latest resource path
    """
    return request.param


@pytest.fixture(scope="session")
def latest_uris():
    """
    Get the URIs of the latest schemas.
    """
    return _LATEST_URIS


@pytest.fixture(scope="session", params=_LATEST_URIS)
def latest_uri(request):
    """
    Get a latest resource URI
    """
    return request.param


@pytest.fixture(scope="session")
def latest_manifest_uri(latest_uris):
    """
    Get the latest manifest URI.
    """
    latest_manifest_uris = tuple(uri for uri in latest_uris if "manifests" in uri)
    assert len(latest_manifest_uris) == 1, "There should be exactly one latest manifest"
    return latest_manifest_uris[0]


@pytest.fixture(scope="session")
def latest_schemas(latest_paths, latest_uris):
    """
    Get the text of the latest schemas.
    """
    return {latest_uri: latest_path.read_text() for latest_uri, latest_path in zip(latest_uris, latest_paths, strict=True)}


@pytest.fixture(scope="session")
def latest_schema_tags(latest_manifest_uri, latest_schemas):
    """
    Get the latest schema tags from the latest manifest.
    """
    tag_entries = yaml.safe_load(latest_schemas[latest_manifest_uri])["tags"]
    schema_tags = {entry["schema_uri"]: entry["tag_uri"] for entry in tag_entries}
    assert len(schema_tags) == len(tag_entries), "There should be no duplicate tags for a schema"
    return schema_tags
