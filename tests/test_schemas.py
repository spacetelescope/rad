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


@pytest.mark.parametrize("schema_uri", SCHEMA_URIS)
def test_required_properties(schema_uri):
    schema = yaml.safe_load(asdf.get_config().resource_manager[schema_uri])
    assert schema["$schema"] == METASCHEMA_URI
    assert "id" in schema
    assert "title" in schema


@pytest.mark.parametrize("schema_uri", SCHEMA_URIS)
def test_schema_style(schema_uri):
    content = asdf.get_config().resource_manager[schema_uri]
    assert content.startswith(b"%YAML 1.1\n---\n")
    assert content.endswith(b"\n...\n")
    assert b"\t" not in content
    assert not any(l != l.rstrip() for l in content.split(b"\n"))


@pytest.mark.parametrize("schema_uri", SCHEMA_URIS)
def test_property_order(schema_uri):
    schema = yaml.safe_load(asdf.get_config().resource_manager[schema_uri])

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


@pytest.mark.parametrize("schema_uri", SCHEMA_URIS)
def test_required(schema_uri):
    schema = yaml.safe_load(asdf.get_config().resource_manager[schema_uri])

    def callback(node):
        if isinstance(node, Mapping) and node.get("type") == "object" and "required" in node:
            property_names = set(node.get("properties", {}).keys())
            required_names = set(node["required"])
            if not required_names.issubset(property_names):
                missing_list = ", ".join(required_names - property_names)
                message = "required references names that do not exist: " + missing_list
                assert False, message

    asdf.treeutil.walk(schema, callback)
