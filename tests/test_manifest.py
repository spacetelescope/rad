"""
Test that the manifest file is correctly structured and refers
to schemas that exist.
"""
import asdf
import pytest
import yaml


@pytest.fixture
def manifest():
    return yaml.safe_load(
        asdf.get_config().resource_manager["asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"]
    )


def test_manifest_valid(manifest):
    schema = asdf.schema.load_schema("asdf://asdf-format.org/core/schemas/extension_manifest-1.0")

    asdf.schema.validate(manifest, schema=schema)

    assert "title" in manifest
    assert "description" in manifest

    for tag in manifest["tags"]:
        # Check that the schema exists:
        assert tag["schema_uri"] in asdf.get_config().resource_manager
        # These are not required by the manifest schema but we're holding ourselves
        # to a higher standard:
        assert "title" in tag
        assert "description" in tag
        assert tag["tag_uri"].startswith("asdf://stsci.edu/datamodels/roman/tags/")
