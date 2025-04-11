"""
Test features of the schemas not covered by the metaschema.
"""

import re
from collections.abc import Mapping

import asdf
import asdf.treeutil
import pytest
import yaml
from crds.config import is_crds_name

from .conftest import MANIFESTS

SCHEMA_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/schemas/"
METASCHEMA_URI = "asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0"
SCHEMA_URIS = tuple(u for u in asdf.get_config().resource_manager if u.startswith(SCHEMA_URI_PREFIX) and u != METASCHEMA_URI)
TAG_DEFS = tuple(tag_def for manifest in MANIFESTS for tag_def in manifest["tags"])
REF_FILE_TAG_DEFS = tuple(tag_def for tag_def in TAG_DEFS if "/reference_files" in tag_def["schema_uri"])
WFI_OPTICAL_ELEMENTS = tuple(
    asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/wfi_optical_element-1.0.0")["enum"]
)
EXPOSURE_TYPE_ELEMENTS = tuple(asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/exposure_type-1.0.0")["enum"])
EXPECTED_COMMON_REFERENCE = {"$ref": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-1.0.0"}
METADATA_FORCING_REQUIRED = ("archive_catalog", "sdf")
ALLOWED_SCHEMA_TAG_VALIDATORS = (
    "tag:stsci.edu:asdf/time/time-1.*",
    "tag:stsci.edu:asdf/core/ndarray-1.*",
    "tag:stsci.edu:asdf/unit/quantity-1.*",
    "tag:stsci.edu:asdf/unit/unit-1.*",
    "tag:astropy.org:astropy/units/unit-1.*",
    "tag:astropy.org:astropy/table/table-1.*",
    "tag:stsci.edu:gwcs/wcs-*",
)


@pytest.fixture(scope="session")
def valid_tag_uris():
    uris = {t["tag_uri"] for manifest in MANIFESTS for t in manifest["tags"]}
    uris.update(ALLOWED_SCHEMA_TAG_VALIDATORS)
    return uris


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema_content(request):
    return asdf.get_config().resource_manager[request.param]


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param])


@pytest.fixture(scope="session", params=REF_FILE_TAG_DEFS)
def ref_file_schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param["schema_uri"]])


@pytest.fixture(scope="session", params=REF_FILE_TAG_DEFS)
def ref_file_uris(request):
    return request.param["tag_uri"], request.param["schema_uri"]


def test_required_properties(schema):
    assert schema["$schema"] == METASCHEMA_URI
    assert "id" in schema
    assert "title" in schema


def test_schema_style(schema_content):
    assert schema_content.startswith(b"%YAML 1.1\n---\n")
    assert schema_content.endswith(b"\n...\n")
    assert b"\t" not in schema_content
    assert not any(line != line.rstrip() for line in schema_content.split(b"\n"))


def test_property_order(schema):
    is_tag_schema = schema["id"] in {t["schema_uri"] for t in TAG_DEFS}

    if is_tag_schema:

        def callback(node):
            if isinstance(node, Mapping) and "propertyOrder" in node:
                assert node.get("type") == "object"
                property_names = set(node.get("properties", {}).keys())
                property_order_names = set(node["propertyOrder"])
                if property_order_names != property_names:
                    missing_list = ", ".join(property_order_names - property_names)
                    extra_list = ", ".join(property_names - property_order_names)
                    message = (
                        "propertyOrder does not match list of properties:\n\n"
                        "missing properties: " + missing_list + "\n"
                        "extra properties: " + extra_list
                    )
                    raise ValueError(message)

        asdf.treeutil.walk(schema, callback)
    else:

        def callback(node):
            if isinstance(node, Mapping):
                assert "propertyOrder" not in node, "Only schemas associated with a tag may specify propertyOrder"

        asdf.treeutil.walk(schema, callback)


def test_required(schema):
    """
    Checks that all properties are required if there is a required list.
    """

    def callback(node):
        if isinstance(node, Mapping) and "required" in node:
            assert node.get("type") == "object"
            property_names = set(node.get("properties", {}).keys())
            required_names = set(node["required"])
            if not required_names.issubset(property_names):
                missing_list = ", ".join(required_names - property_names)
                message = "required references names that do not exist: " + missing_list
                raise ValueError(message)

    asdf.treeutil.walk(schema, callback)


def test_metadata_force_required(schema):
    """
    Test that if certain properties have certain metadata entries, that they are in a required list.
    """
    xfail_uris = (
        "asdf://stsci.edu/datamodels/roman/schemas/tvac/groundtest-1.0.0",
        "asdf://stsci.edu/datamodels/roman/schemas/tvac/ref_file-1.0.0",
        "asdf://stsci.edu/datamodels/roman/schemas/fps/ref_file-1.0.0",
    )
    if schema["id"] in xfail_uris:
        pytest.xfail(
            reason=f"{schema['id']} is not being altered to ensure required lists for archive metadata, "
            "due to it being in either tvac or fps."
        )

    def callback(node):
        if isinstance(node, Mapping) and "properties" in node:
            for prop_name, prop in node["properties"].items():
                # Test that if a subnode has a required list, that the parent has a required list
                if isinstance(prop, Mapping) and "required" in prop:
                    assert "required" in node
                    assert prop_name in node["required"]

                # Test that if a subnode has certain metadata entries, that the parent has a required list
                for metadata in METADATA_FORCING_REQUIRED:
                    if isinstance(prop, Mapping) and metadata in prop:
                        assert "required" in node, f"metadata {metadata} in {prop_name} requires required list"
                        assert prop_name in node["required"]

    asdf.treeutil.walk(schema, callback)


def test_flowstyle(schema):
    is_tag_schema = False

    for manifest in MANIFESTS:
        if is_tag_schema := schema["id"] in {t["schema_uri"] for t in manifest["tags"]}:
            break

    if is_tag_schema:
        found_flowstyle = False

        def callback(node):
            nonlocal found_flowstyle
            if isinstance(node, Mapping) and node.get("flowStyle") == "block":
                found_flowstyle = True

        asdf.treeutil.walk(schema, callback)

        assert found_flowstyle, "Schemas associated with a tag must specify flowStyle: block"
    else:

        def callback(node):
            if isinstance(node, Mapping):
                assert "flowStyle" not in node, "Only schemas associated with a tag may specify flowStyle"

        asdf.treeutil.walk(schema, callback)


def test_tag(schema, valid_tag_uris):
    def callback(node):
        if isinstance(node, Mapping) and "tag" in node:
            assert node["tag"] in valid_tag_uris

    asdf.treeutil.walk(schema, callback)


def _model_name_from_schema_uri(schema_uri):
    schema_name = schema_uri.split("/")[-1].split("-")[0]
    class_name = "".join([p.capitalize() for p in schema_name.split("_")])
    if schema_uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/reference_files/"):
        class_name += "Ref"

    if class_name not in ["WfiWcs"]:  # Names to be unmodified
        if class_name.startswith("Wfi") and "Ref" not in class_name:
            class_name = class_name.split("Wfi")[-1]
        elif class_name.startswith("MatableRef"):
            class_name = "MATableRef" + class_name.split("MatableRef")[-1]

    return f"{class_name}Model"


def test_datamodel_name(schema):
    if "datamodel_name" in schema:
        assert _model_name_from_schema_uri(schema["id"]) == schema["datamodel_name"]


# Confirm that the optical_element filter in wfi_img_photom.yml matches WFI_OPTICAL_ELEMENTS
def test_matched_optical_element_entries():
    phot_table_keys = list(
        asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/reference_files/wfi_img_photom-1.0.0")["properties"][
            "phot_table"
        ]["patternProperties"]
    )
    r = re.compile(phot_table_keys[0])
    for element_str in WFI_OPTICAL_ELEMENTS:
        assert r.search(element_str)


def test_matched_p_exptype_entries():
    """Confirm that the p_keyword version of exposure type match the enum version."""
    p_exptype = asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type-1.0.0")[
        "properties"
    ]["exposure"]["properties"]["p_exptype"]["pattern"]
    r = re.compile(p_exptype)
    for element_str in EXPOSURE_TYPE_ELEMENTS:
        assert r.search(element_str + "|")


def _find_ndarrays(key, schema):
    """
    Find all the ndarray entries in the schema
    """
    entries = []
    if isinstance(schema, dict):
        for new_key, value in schema.items():
            if isinstance(value, str) and value.startswith("tag:stsci.edu:asdf/core/ndarray-"):
                entries.append((key,))
            else:
                entries.extend((key, *key_) for key_ in _find_ndarrays(new_key, value))
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            entries.extend((key, *key_) for key_ in _find_ndarrays(index, value))

    return entries


def _get_ndarray_entry(schema, entry):
    """
    Get the ndarray portion of the schema for the entry
    """
    current = schema

    for key in entry[1:]:
        current = current[key]

    return current


def test_exact_datatype(schema):
    """Confirm that `exact_datatype` is defined for all arrays"""
    entries = _find_ndarrays("", schema)

    if entries:
        for entry in entries:
            if "datatype" in (ndarray_entry := _get_ndarray_entry(schema, entry)):
                assert "exact_datatype" in ndarray_entry, f"extact_datatype needed for {'.'.join(entry[1:])}"
                assert ndarray_entry["exact_datatype"] is True
            else:
                raise ValueError(f"datatype not found for {'.'.join(entry[1:])}")


def _get_reftype(schema):
    """
    Extract the reftype from the schema
    """
    all_of = schema["properties"]["meta"]["allOf"]

    for sub_schema in all_of:
        if "properties" in sub_schema:
            return sub_schema["properties"]["reftype"]["enum"][0]


def test_reftype(ref_file_schema):
    """
    Check that the reftype is valid for CRDS
    """
    reftype = _get_reftype(ref_file_schema)
    assert is_crds_name(f"roman_wfi_{reftype.lower()}_0000.asdf")


def test_reftype_tag(ref_file_uris):
    """
    Check that the URIs match the reftype for a valid CRDS check
    """
    tag_uri = ref_file_uris[0]
    schema_uri = ref_file_uris[1]

    schema = yaml.safe_load(asdf.get_config().resource_manager[schema_uri])
    reftype = _get_reftype(schema).lower()

    assert asdf.util.uri_match(f"asdf://stsci.edu/datamodels/roman/tags/reference_files/*{reftype}-*", tag_uri)
    assert asdf.util.uri_match(f"asdf://stsci.edu/datamodels/roman/schemas/reference_files/*{reftype}-*", schema_uri)


def test_ref_file_meta_common(ref_file_schema):
    """
    Test that the meta for all reference files contains a reference to `ref_common`
    """
    all_of = ref_file_schema["properties"]["meta"]["allOf"]

    if ref_file_schema["id"].find("skycells") >= 0:
        return

    for item in all_of:
        if item == EXPECTED_COMMON_REFERENCE:
            break
    else:
        raise ValueError("ref_common not found in meta")


# don't test tvac or fps schemas as they are static
@pytest.mark.parametrize(
    "uri",
    [
        uri
        for uri in SCHEMA_URIS
        if not uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/fps/")
        and not uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/tvac/")
    ],
)
def test_varchar_length(uri):
    """
    Test that varchar(N) in archive_metadata for string objects
    has a matching maxLength: N validation keyword
    """
    schema = asdf.schema.load_schema(uri)

    def callback(node, nvarchars=None):
        nvarchars = nvarchars or {}
        if not isinstance(node, dict):
            return
        if node.get("type", "") != "string":
            return
        if "archive_catalog" not in node:
            return
        m = re.match(r"^nvarchar\(([0-9]+)\)$", node["archive_catalog"]["datatype"])
        if not m:
            return
        v = int(m.group(1))
        assert "maxLength" in node, f"archive_catalog has nvarchar, schema {uri} is missing maxLength"
        assert node["maxLength"] == v, f"archive_catalog nvarchar does not match maxLength in schema {uri}"

    asdf.treeutil.walk(schema, callback)


@pytest.mark.parametrize("uri", SCHEMA_URIS)
def test_ref_loneliness(uri):
    """
    An object with a $ref should contain no other items
    """
    schema = asdf.schema.load_schema(uri)

    def callback(node):
        if not isinstance(node, dict):
            return
        if "$ref" not in node:
            return
        assert len(node) == 1

    asdf.treeutil.walk(schema, callback)


@pytest.mark.parametrize("uri", SCHEMA_URIS)
def test_absolute_ref(uri):
    """
    Test that all $ref are absolute URIs matching those registered with ASDF
    """
    schema = asdf.schema.load_schema(uri)
    resources = asdf.config.get_config().resource_manager

    def callback(node):
        if not isinstance(node, dict):
            return
        if "$ref" not in node:
            return

        # Check that the $ref is a full URI registered with ASDF
        assert node["$ref"] in resources

    asdf.treeutil.walk(schema, callback)
