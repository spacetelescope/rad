"""
Test that the manifest file is correctly structured and refers
to schemas that exist.
"""

import asdf

from .conftest import MANIFEST_URI_PREFIX, RAD_URI_PREFIX, SCHEMA_URI_PREFIX, TAG_URI_PREFIX


def test_manifest_valid(manifest):
    """
    Validate the manifest file against the asdf schema for extension manifests.
    """
    schema = asdf.schema.load_schema("asdf://asdf-format.org/core/schemas/extension_manifest-1.0.0")

    asdf.schema.validate(manifest, schema=schema)

    assert "title" in manifest
    assert "description" in manifest


def test_manifest_uris(manifest):
    """
    Check that the two URIs in the manifest are consistent with each other
        That is check that the uri suffixes are the same for the id and the extension_uri
    """
    uri_suffix = manifest["id"].split(MANIFEST_URI_PREFIX)[-1]
    extension_uri_suffix = manifest["extension_uri"].split(f"{RAD_URI_PREFIX}extensions/")[-1]

    assert uri_suffix == extension_uri_suffix


def test_manifest_entries(manifest_entry):
    """
    Check that the manifest entries are valid and consistent
    """
    # Check that the schema exists:
    assert manifest_entry["schema_uri"] in asdf.get_config().resource_manager
    # These are not required by the manifest schema but we're holding ourselves
    # to a higher standard:
    assert "title" in manifest_entry
    assert "description" in manifest_entry

    # Check the URIs
    assert manifest_entry["tag_uri"].startswith(TAG_URI_PREFIX)
    uri_suffix = manifest_entry["tag_uri"].split(TAG_URI_PREFIX)[-1]
    # Remove tagged scalars from the uri string
    schema_uri = manifest_entry["schema_uri"]
    if "tagged_scalars" in schema_uri.split("/"):
        schema_uri = schema_uri.replace("tagged_scalars/", "")
    assert schema_uri.endswith(uri_suffix)
    assert schema_uri.startswith(SCHEMA_URI_PREFIX)
