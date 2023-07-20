"""
Test features of the schemas not covered by the metaschema.
"""
import re
from collections.abc import Mapping

import asdf
import pytest
import yaml
from crds.config import is_crds_name

from .conftest import MANIFEST

SCHEMA_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/schemas/"
METASCHEMA_URI = "asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0"
SCHEMA_URIS = [u for u in asdf.get_config().resource_manager if u.startswith(SCHEMA_URI_PREFIX) and u != METASCHEMA_URI]
REF_FILE_SCHEMA_URIS = [u["schema_uri"] for u in MANIFEST["tags"] if "/reference_files/" in u["schema_uri"]]
WFI_OPTICAL_ELEMENTS = list(
    asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/wfi_optical_element-1.0.0")["enum"]
)
EXPOSURE_TYPE_ELEMENTS = list(asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/exposure_type-1.0.0")["enum"])


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema_content(request):
    return asdf.get_config().resource_manager[request.param]


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param])


@pytest.fixture(scope="session", params=REF_FILE_SCHEMA_URIS)
def ref_file_schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param])


@pytest.fixture(scope="session", params=[entry for entry in MANIFEST["tags"] if "/reference_files/" in entry["schema_uri"]])
def ref_file_uris(request):
    return request.param["tag_uri"], request.param["schema_uri"]


@pytest.fixture(scope="session")
def valid_tag_uris(manifest):
    uris = {t["tag_uri"] for t in manifest["tags"]}
    uris.update(
        [
            "tag:stsci.edu:asdf/time/time-1.1.0",
            "tag:stsci.edu:asdf/core/ndarray-1.0.0",
            "tag:stsci.edu:asdf/unit/quantity-1.1.0",
            "tag:stsci.edu:asdf/unit/unit-1.0.0",
            "tag:astropy.org:astropy/units/unit-1.0.0",
        ]
    )
    return uris


def test_required_properties(schema):
    assert schema["$schema"] == METASCHEMA_URI
    assert "id" in schema
    assert "title" in schema


def test_schema_style(schema_content):
    assert schema_content.startswith(b"%YAML 1.1\n---\n")
    assert schema_content.endswith(b"\n...\n")
    assert b"\t" not in schema_content
    assert not any(line != line.rstrip() for line in schema_content.split(b"\n"))


def test_property_order(schema, manifest):
    is_tag_schema = schema["id"] in {t["schema_uri"] for t in manifest["tags"]}

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
                    assert False, message

        asdf.treeutil.walk(schema, callback)
    else:

        def callback(node):
            if isinstance(node, Mapping):
                assert "propertyOrder" not in node, "Only schemas associated with a tag may specify propertyOrder"

        asdf.treeutil.walk(schema, callback)


def test_required(schema):
    def callback(node):
        if isinstance(node, Mapping) and "required" in node:
            assert node.get("type") == "object"
            property_names = set(node.get("properties", {}).keys())
            required_names = set(node["required"])
            if not required_names.issubset(property_names):
                missing_list = ", ".join(required_names - property_names)
                message = "required references names that do not exist: " + missing_list
                assert False, message

    asdf.treeutil.walk(schema, callback)


def test_flowstyle(schema, manifest):
    is_tag_schema = schema["id"] in {t["schema_uri"] for t in manifest["tags"]}

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

    if class_name.startswith("Wfi") and "Ref" not in class_name:
        class_name = class_name.split("Wfi")[-1]

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


# Confirm that the p_keyword version of exposure type match the enum version
def test_matched_p_exptype_entries():
    p_exptype = asdf.schema.load_schema("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type-1.0.0")[
        "properties"
    ]["exposure"]["properties"]["p_exptype"]["pattern"]
    r = re.compile(p_exptype)
    for element_str in EXPOSURE_TYPE_ELEMENTS:
        assert r.search(element_str + "|")


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
