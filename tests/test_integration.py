"""
Test that the asdf library integration is working properly.
"""

import importlib.resources as importlib_resources

import asdf
import pytest
import yaml

from rad import resources


def test_manifest_integration(manifest_path, manifest_uris):
    """
    Check that the manifest is properly integrated with the asdf library.
    """
    content = manifest_path.read_bytes()
    manifest = yaml.safe_load(content)
    uri = manifest["id"]

    assert uri in manifest_uris
    assert content == asdf.get_config().resource_manager[uri]


def test_schema_integration(schema_path, schema_uris, metaschema_uri):
    """
    Check that the schema is properly integrated with the asdf library.
    """
    content = schema_path.read_bytes()
    schema = yaml.safe_load(content)
    uri = schema["id"]

    # If the schema is in the SSC directory then it should not be available through
    # ASDF
    if "SSC" in str(schema_path):
        assert uri not in schema_uris and uri != metaschema_uri
        with pytest.raises(KeyError, match=r"Resource unavailable for URI: .*"):
            asdf.get_config().resource_manager[uri]
    else:
        assert uri in schema_uris or uri == metaschema_uri
        assert content == asdf.get_config().resource_manager[uri]


def test_schema_filename(schema_path):
    """
    Check the filename pattern aligns with the schema ID.
    """
    schema = yaml.safe_load(schema_path.read_bytes())
    id_suffix = str(schema_path.with_suffix("")).split(str(importlib_resources.files(resources)))[-1]
    assert schema["id"].endswith(id_suffix)
