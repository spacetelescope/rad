"""
Test features of the schemas not covered by the metaschema.
"""
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
