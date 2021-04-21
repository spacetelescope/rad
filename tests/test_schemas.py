"""
Test features of the schemas not covered by the metaschema.
"""
from collections.abc import Mapping

import asdf
import pytest
import yaml


SCHEMA_URI_PREFIX = "asdf://stsci.edu/datamodels/roman/schemas/"
METASCHEMA_URI = "asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0"
SCHEMA_URIS = [
    u for u in asdf.get_config().resource_manager
    if u.startswith(SCHEMA_URI_PREFIX) and u != METASCHEMA_URI
]


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema_content(request):
    return asdf.get_config().resource_manager[request.param]


@pytest.fixture(scope="session", params=SCHEMA_URIS)
def schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param])


@pytest.fixture(scope="session", params=[u for u in SCHEMA_URIS if u.split("/")[-1] not in ["ref_common-1.0.0", "common-1.0.0"]])
def tag_schema(request):
    return yaml.safe_load(asdf.get_config().resource_manager[request.param])


@pytest.fixture(scope="session")
def valid_tag_uris(manifest):
    uris = {t["tag_uri"] for t in manifest["tags"]}
    uris.update([
        "tag:stsci.edu:asdf/time/time-1.1.0",
        "tag:stsci.edu:asdf/core/ndarray-1.0.0",
    ])
    return uris


def test_required_properties(schema):
    assert schema["$schema"] == METASCHEMA_URI
    assert "id" in schema
    assert "title" in schema


def test_schema_style(schema_content):
    assert schema_content.startswith(b"%YAML 1.1\n---\n")
    assert schema_content.endswith(b"\n...\n")
    assert b"\t" not in schema_content
    assert not any(l != l.rstrip() for l in schema_content.split(b"\n"))


def test_property_order(schema):
    def callback(node):
        if isinstance(node, Mapping) and node.get("type") == "object" and "propertyOrder" in node:
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


def test_required(schema):
    def callback(node):
        if isinstance(node, Mapping) and node.get("type") == "object" and "required" in node:
            property_names = set(node.get("properties", {}).keys())
            required_names = set(node["required"])
            if not required_names.issubset(property_names):
                missing_list = ", ".join(required_names - property_names)
                message = "required references names that do not exist: " + missing_list
                assert False, message

    asdf.treeutil.walk(schema, callback)


def test_flowstyle(tag_schema):
    def callback(node):
        if isinstance(node, Mapping) and node.get("type") == "object":
            assert node.get("flowStyle") == "block", "all objects require flowStyle: block"

    asdf.treeutil.walk(tag_schema, callback)


def test_tag(schema, valid_tag_uris):
    def callback(node):
        if isinstance(node, Mapping) and "tag" in node:
            assert node["tag"] in valid_tag_uris

    asdf.treeutil.walk(schema, callback)
