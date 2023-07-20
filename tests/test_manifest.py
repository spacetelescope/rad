"""
Test that the manifest file is correctly structured and refers
to schemas that exist.
"""
import asdf
import pytest

from .conftest import MANIFEST


def test_manifest_valid(manifest):
    schema = asdf.schema.load_schema("asdf://asdf-format.org/core/schemas/extension_manifest-1.0.0")

    asdf.schema.validate(manifest, schema=schema)

    assert "title" in manifest
    assert "description" in manifest


@pytest.mark.parametrize("entry", MANIFEST["tags"])
def test_manifest_entries(entry):
    # Check that the schema exists:
    assert entry["schema_uri"] in asdf.get_config().resource_manager
    # These are not required by the manifest schema but we're holding ourselves
    # to a higher standard:
    assert "title" in entry
    assert "description" in entry

    # Check the URIs
    assert entry["tag_uri"].startswith("asdf://stsci.edu/datamodels/roman/tags/")
    uri_suffix = entry["tag_uri"].split("asdf://stsci.edu/datamodels/roman/tags/")[-1]
    assert entry["schema_uri"].endswith(uri_suffix)
    assert entry["schema_uri"].startswith("asdf://stsci.edu/datamodels/roman/schemas/")
