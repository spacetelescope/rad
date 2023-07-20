"""
Test that the asdf library integration is working properly.
"""
import sys

if sys.version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources

import asdf
import pytest
import yaml

from rad import resources


@pytest.mark.parametrize("manifest_path", (importlib_resources.files(resources) / "manifests").glob("**/*.yaml"))
def test_manifest_integration(manifest_path):
    content = manifest_path.read_bytes()
    manifest = yaml.safe_load(content)
    asdf_content = asdf.get_config().resource_manager[manifest["id"]]
    assert asdf_content == content


@pytest.mark.parametrize("schema_path", (importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
def test_schema_integration(schema_path):
    content = schema_path.read_bytes()
    schema = yaml.safe_load(content)
    asdf_content = asdf.get_config().resource_manager[schema["id"]]
    assert asdf_content == content


@pytest.mark.parametrize("schema_path", (importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
def test_schema_filename(schema_path):
    """
    Check the filename pattern aligns with the schema ID.
    """
    schema = yaml.safe_load(schema_path.read_bytes())
    id_suffix = str(schema_path.with_suffix("")).split(str(importlib_resources.files(resources)))[-1]
    assert schema["id"].endswith(id_suffix)
