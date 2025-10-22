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

# Defined directly so that the value can be reused to find the URIs from the ASDF resource manager
# outside of a pytest fixture
_RAD_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/"
_MANIFEST_URI_PREFIX = f"{_RAD_URI_PREFIX}manifests/"
_SCHEMA_URI_PREFIX = f"{_RAD_URI_PREFIX}schemas/"
_METASCHEMA_URI = f"{_SCHEMA_URI_PREFIX}rad_schema-1.0.0"


# Get all the schema URIs from the ASDF resource manager cached to the current session
# to avoid loading them multiple times
_MANIFEST_URIS = tuple(uri for uri in asdf.get_config().resource_manager if uri.startswith(_MANIFEST_URI_PREFIX))
_SCHEMA_URIS = tuple(u for u in asdf.get_config().resource_manager if u.startswith(_SCHEMA_URI_PREFIX) and u != _METASCHEMA_URI)
_URIS = _SCHEMA_URIS + _MANIFEST_URIS + (_METASCHEMA_URI,)

# load all the schemas from the ASDF resource manager
_CURRENT_CONTENT = MappingProxyType({uri: asdf.get_config().resource_manager[uri] for uri in _URIS})
_CURRENT_RESOURCES = MappingProxyType({uri: yaml.safe_load(content) for uri, content in _CURRENT_CONTENT.items()})
_MANIFEST_ENTRIES = tuple(chain(*[_CURRENT_RESOURCES[uri]["tags"] for uri in _MANIFEST_URIS]))


# Look directly at the latest schemas storage directory to infer latest schemas
_LATEST_DIR = Path(__file__).parent.parent.absolute() / "latest"
_LATEST_PATHS = MappingProxyType(
    {latest_path: yaml.safe_load(latest_path.read_bytes()) for latest_path in _LATEST_DIR.glob("**/*.yaml")}
)
_LATEST_TOP_LEVEL_PATHS = tuple(latest_path for latest_path in _LATEST_PATHS if latest_path.parent == _LATEST_DIR)
_LATEST_URI_PATHS = MappingProxyType({schema["id"]: path for path, schema in _LATEST_PATHS.items()})
_LATEST_URIS = tuple(_LATEST_URI_PATHS.keys())
_LATEST_MANIFEST_URIS = tuple(uri for uri in _LATEST_URIS if "manifests" in uri)
_LATEST_MANIFEST_TAGS = MappingProxyType(
    {uri: tuple(entry["tag_uri"] for entry in _CURRENT_RESOURCES[uri]["tags"]) for uri in _LATEST_MANIFEST_URIS}
)
_LATEST_DATAMODELS_URI = next(uri for uri in _LATEST_MANIFEST_URIS if "static" not in uri)
_LATEST_STATIC_URI = next(uri for uri in _LATEST_MANIFEST_URIS if "static" in uri)
_LATEST_DATAMODEL_URIS = tuple(uri["schema_uri"] for uri in _CURRENT_RESOURCES[_LATEST_DATAMODELS_URI]["tags"])
_LATEST_ARCHIVE_URIS = tuple(schema["id"] for schema in _LATEST_PATHS.values() if "archive_meta" in schema)


def _find_latest(uris):
    version = Version("0.0.0")
    uri = None
    latest_uri = None
    for uri in uris:
        if version < (new := Version("1.0.0" if (v := uri.split("-")[-1]) == "1.0" else v)):
            version = new
            latest_uri = uri
    return latest_uri


_PREVIOUS_DATAMODELS_URI = _find_latest(
    [uri for uri in _MANIFEST_URIS if "static" not in uri and "datamodels" in uri and uri != _LATEST_DATAMODELS_URI]
)


### Fixtures for directly accessing resources via Python
@pytest.fixture(scope="session", params=(importlib_resources.files(resources) / "manifests").glob("**/*.yaml"))
def manifest_path(request):
    """
    Get a path to a manifest file directly from the python package, rather than ASDF
    """
    return request.param


@pytest.fixture(scope="session", params=(importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
def schema_path(request):
    """
    Get a path to a schema file directly from the python package, rather than ASDF
    """
    return request.param


@pytest.fixture(scope="session", params=(importlib_resources.files(resources) / "schemas" / "SSC").glob("**/*.yaml"))
def ssc_schema_path(request):
    """
    Get a path to an SSC schema file directly from the python package, rather than ASDF
    """
    return request.param


@pytest.fixture(scope="session")
def ssc_schema_uri(ssc_schema_path):
    """
    Get a URI for an SSC schema
    """
    content = ssc_schema_path.read_bytes()
    schema = yaml.safe_load(content)
    return schema["id"]


### Fixtures for working with only the latest schemas
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


@pytest.fixture(scope="session", params=_LATEST_ARCHIVE_URIS)
def latest_archive_uri(request):
    """
    Get a latest archive resource URI
    """
    return request.param


@pytest.fixture(scope="session")
def latest_dir():
    """
    Get the path to the latest directory.
    """
    return _LATEST_DIR


@pytest.fixture(scope="session")
def latest_reference_files_dir(latest_dir):
    """
    Get the path to the latest reference files directory.
    """
    return latest_dir / "reference_files"


@pytest.fixture(scope="session")
def latest_ccsp_dir(latest_dir):
    """
    Get the path to the latest CCSP schemas directory.
    """
    return latest_dir / "CCSP"


@pytest.fixture(scope="session", params=_LATEST_TOP_LEVEL_PATHS)
def latest_top_level_path(request):
    """
    Get a path to one of the top level latest schemas.
    """
    return request.param


@pytest.fixture(scope="session")
def latest_uri_paths():
    """
    Get the mapping of latest URIs to their paths.
    """
    return _LATEST_URI_PATHS


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
def latest_datamodels_uri():
    """
    Get the latest (datamodels) manifest URI.
    """
    assert len(_LATEST_MANIFEST_URIS) == 2, f"There should be exactly two latest manifests, found {len(_LATEST_MANIFEST_URIS)}"
    return _LATEST_DATAMODELS_URI


@pytest.fixture(scope="session", params=_LATEST_DATAMODEL_URIS)
def latest_tagged_schema_uri(request):
    """Get a latest tagged schema URI"""
    return request.param


@pytest.fixture(scope="session", params=_LATEST_MANIFEST_TAGS[_LATEST_DATAMODELS_URI])
def latest_datamodels_tag_uri(request):
    """
    Get a latest datamodels tag URI
    """
    return request.param


@pytest.fixture(scope="session")
def latest_static_uri():
    """
    Get the latest (static) manifest URI.
    """
    assert len(_LATEST_MANIFEST_URIS) == 2, f"There should be exactly two latest manifests, found {len(_LATEST_MANIFEST_URIS)}"
    return _LATEST_STATIC_URI


@pytest.fixture(scope="session")
def latest_static_tags(latest_static_uri):
    """
    Get the latest static tags
    """

    return _LATEST_MANIFEST_TAGS[latest_static_uri]


@pytest.fixture(scope="session", params=_LATEST_MANIFEST_TAGS[_LATEST_STATIC_URI])
def latest_static_tag_uri(request):
    """
    Get a latest static tag URI
    """
    return request.param


@pytest.fixture(scope="session")
def latest_schemas(latest_paths, latest_uris):
    """
    Get the text of the latest schemas.
    """
    return {latest_uri: latest_path.read_text() for latest_uri, latest_path in zip(latest_uris, latest_paths, strict=True)}


@pytest.fixture(scope="session", params=tuple(entry["tag_uri"] for entry in _CURRENT_RESOURCES[_PREVIOUS_DATAMODELS_URI]["tags"]))
def previous_datamodels_tag(request):
    """
    Get a tag in the previous datamodel
    """
    return request.param


@pytest.fixture(scope="session")
def latest_schema_tags(latest_datamodels_uri, latest_schemas):
    """
    Get the latest schema tags from the latest manifest.
    """
    tag_entries = yaml.safe_load(latest_schemas[latest_datamodels_uri])["tags"]
    schema_tags = {entry["schema_uri"]: entry["tag_uri"] for entry in tag_entries}
    assert len(schema_tags) == len(tag_entries), "There should be no duplicate tags for a schema"
    return schema_tags


@pytest.fixture(scope="session")
def latest_schema_tag_prefixes(latest_schema_tags):
    """
    Get the prefixes of the latest schema tags from the latest manifest.
    """
    return set(value.split("-")[0] for value in latest_schema_tags.values())


### Fixtures for working with the schema URIs directly
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
    """
    Get the schema URI prefix.
    """
    return _SCHEMA_URI_PREFIX


@pytest.fixture(scope="session")
def metaschema_uri():
    """
    Get the metaschema URI.
    """
    return _METASCHEMA_URI


@pytest.fixture(scope="session")
def tag_uri_prefix(rad_uri_prefix):
    """
    Get the tag URI prefix.
    """
    return f"{rad_uri_prefix}tags/"


### Fixtures for working with any type of resource
@pytest.fixture(scope="session")
def uris():
    """
    Get all the URIs of RAD from the ASDF resource manager.
    """
    return _URIS


@pytest.fixture(scope="session", params=_URIS)
def uri(request):
    """
    Get a URI for RAD from the ASDF resource manager.
    """
    return request.param


### Fixtures for working with the manifest resources
@pytest.fixture(scope="session")
def manifest_uris():
    """
    Get the manifest URIs for RAD.
    """
    return _MANIFEST_URIS


@pytest.fixture(scope="session", params=_MANIFEST_URIS)
def manifest_uri(request):
    """
    Get a URI for a manifest from the ASDF resource manager.
    """
    return request.param


### Fixtures for working with the schema resources
@pytest.fixture(scope="session")
def schema_uris():
    """
    Get the schema URIs for RAD from the ASDF resource manager.
    """
    return _SCHEMA_URIS


@pytest.fixture(scope="session", params=tuple(uri for uri in _LATEST_URIS if uri in _SCHEMA_URIS))
def schema_uri(request):
    """
    Get a URI for a RAD schema from the ASDF resource manager.

    Note
    ----
    Since the schemas are versioned, fixed schema versions cannot be modified so they are
    not returned by this fixture.
    """
    return request.param


@pytest.fixture(scope="session", params=tuple(uri for uri in _LATEST_URIS if "/reference_files" in uri and uri in _SCHEMA_URIS))
def ref_file_uri(request):
    """
    Get a URI related to the RAD reference files from the ASDF resource manager.
    """
    return request.param


@pytest.fixture(scope="session", params=tuple(uri for uri in _LATEST_URIS if "/CCSP" in uri and uri in _SCHEMA_URIS))
def ccsp_uri(request):
    """
    Get a URI related to the RAD CCSP schemas.
    """
    return request.param


@pytest.fixture(scope="session", params=tuple(uri for uri in _LATEST_DATAMODEL_URIS if "/CCSP" in uri))
def ccsp_model_uri(request):
    """
    Get a URI related to the RAD CCSP modelschemas.
    """
    return request.param


### Fixtures for working with the information within the resources
@pytest.fixture(scope="session")
def current_content(uri):
    """
    Get the current file content from the ASDF resource manager.
    """
    return _CURRENT_CONTENT[uri]


@pytest.fixture(scope="session")
def current_resources():
    """
    Get the current resources (loaded yaml items) from the ASDF resource manager.
    """
    return _CURRENT_RESOURCES


@pytest.fixture(scope="session")
def manifest(manifest_uri, current_resources):
    """
    Get a manifest resource for RAD from the ASDF resource manager.
    """
    return current_resources[manifest_uri]


@pytest.fixture(scope="session")
def schema(schema_uri, current_resources):
    """
    Get a schema resource for RAD from the ASDF resource manager.
    """
    return current_resources[schema_uri]


@pytest.fixture(scope="session")
def ref_file_schema(ref_file_uri, current_resources):
    """
    Get a reference file schema resource for RAD from the ASDF resource manager.
    """
    return current_resources[ref_file_uri]


@pytest.fixture(scope="session")
def ccsp_schema(ccsp_uri, current_resources):
    """
    Get a CCSP schema.
    """
    return current_resources[ccsp_uri]


@pytest.fixture(scope="session")
def ccsp_model_schema(ccsp_model_uri, current_resources):
    """
    Get a CCSP model schema.
    """
    return current_resources[ccsp_model_uri]


### Fixtures for working with the content within the manifests like tags
@pytest.fixture(scope="session")
def manifest_entries():
    """
    Get the manifest entries.
    """
    return _MANIFEST_ENTRIES


@pytest.fixture(scope="session", params=_MANIFEST_ENTRIES)
def manifest_entry(request):
    """
    Get an entry from a manifest.
    """
    return request.param


@pytest.fixture(scope="session")
def manifest_by_schema(manifest_uris, current_resources):
    """
    Get the maps of schema_uris to tag_uris for a given manifest
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
    Get the maps of tag_uris to schema_uris for a given manifest
    """
    return MappingProxyType(
        {uri: MappingProxyType({value: key for key, value in entry.items()}) for uri, entry in manifest_by_schema.items()}
    )


@pytest.fixture(scope="session")
def schema_tag_map(manifest_by_schema):
    """
    Get a total map of any schema URI to any tag URI
    """
    return MappingProxyType(
        {schema_uri: tag_uri for schema_tag_map in manifest_by_schema.values() for schema_uri, tag_uri in schema_tag_map.items()}
    )


@pytest.fixture(scope="session")
def tag_schema_map(schema_tag_map):
    """
    Get a total map of any tag URI to any schema URI
    """
    return MappingProxyType({tag_uri: schema_uri for schema_uri, tag_uri in schema_tag_map.items()})


@pytest.fixture(scope="session")
def datamodel_tag_uris(current_resources, manifest_uris):
    """
    Get the set of all tags defined in any datamodels manifest
    """
    return frozenset(
        chain(*[[entry["tag_uri"] for entry in current_resources[uri]["tags"]] for uri in manifest_uris if "static" not in uri])
    )


@pytest.fixture(scope="session")
def tagged_schema_uris(manifest_entries):
    """
    Get the tags from the manifest entries.
    """
    return frozenset(entry["schema_uri"] for entry in manifest_entries)


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
    """
    Get the set of all things that can be used under a tag: keyword
    """
    uris = set(entry["tag_uri"] for entry in manifest_entries)
    uris.update(allowed_schema_tag_validators)
    return frozenset(uris)


### Fixtures for working with reading regex patterns from the schemas
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

    return _find_latest(uris)


_PHOT_TABLE_KEY_PATTERNS = _CURRENT_RESOURCES[
    _get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/reference_files/wfi_img_photom")
]["properties"]["phot_table"]["patternProperties"]
_OPTICAL_ELEMENTS = tuple(
    _CURRENT_RESOURCES[_get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/wfi_optical_element")]["enum"]
)
_EXPOSURE_TYPE_ELEMENTS = tuple(
    _CURRENT_RESOURCES[_get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/exposure_type")]["enum"]
)
_P_EXPTYPE_PATTERN = _CURRENT_RESOURCES[
    _get_latest_uri("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type")
]["properties"]["exposure"]["properties"]["p_exptype"]["pattern"]


@pytest.fixture(scope="session")
def phot_table_key_patterns():
    """
    Get the pattern for the photometry table key used by the reference files.
    """
    return tuple(compile(pattern) for pattern in _PHOT_TABLE_KEY_PATTERNS.keys())


@pytest.fixture(
    scope="session",
    params=tuple(p for pattern in _PHOT_TABLE_KEY_PATTERNS.keys() for p in pattern.split(")$")[0].split("(")[-1].split("|")),
)
def phot_table_key(request):
    """
    Get the photometry table key from the request.
    """
    return request.param


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


@pytest.fixture(scope="class")
def asdf_ssc_config():
    """
    Fixture to load the SSC schemas into asdf for testing
    """
    from rad._parser._ssc import asdf_ssc_config

    with asdf_ssc_config():
        yield
