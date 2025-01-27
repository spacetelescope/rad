"""
Test that the manifest file is correctly structured and refers
to schemas that exist.
"""

import asdf


def test_manifest_valid(manifest):
    schema = asdf.schema.load_schema("asdf://asdf-format.org/core/schemas/extension_manifest-1.0.0")

    asdf.schema.validate(manifest, schema=schema)

    assert "title" in manifest
    assert "description" in manifest


def test_manifest_entries(manifest_entry):
    # Check that the schema exists:
    assert manifest_entry["schema_uri"] in asdf.get_config().resource_manager
    # These are not required by the manifest schema but we're holding ourselves
    # to a higher standard:
    assert "title" in manifest_entry
    assert "description" in manifest_entry

    # Check the URIs
    assert manifest_entry["tag_uri"].startswith("asdf://stsci.edu/datamodels/roman/tags/")
    uri_suffix = manifest_entry["tag_uri"].split("asdf://stsci.edu/datamodels/roman/tags/")[-1]
    # Remove tagged scalars from the uri string
    schema_uri = manifest_entry["schema_uri"]
    if "tagged_scalars" in schema_uri.split("/"):
        schema_uri = schema_uri.replace("tagged_scalars/", "")
    assert schema_uri.endswith(uri_suffix)
    assert schema_uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/")
