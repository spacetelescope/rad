"""
Test that the manifest file is correctly structured and refers
to schemas that exist.
"""

import asdf


def test_manifest_valid(manifest):
    """
    Validate the manifest file against the asdf schema for extension manifests.
    """
    schema = asdf.schema.load_schema("asdf://asdf-format.org/core/schemas/extension_manifest-1.0.0")

    asdf.schema.validate(manifest, schema=schema)

    assert "title" in manifest
    assert "description" in manifest


def test_manifest_uris(manifest, rad_uri_prefix, manifest_uri_prefix):
    """
    Check that the two URIs in the manifest are consistent with each other
        That is check that the uri suffixes are the same for the id and the extension_uri
    """
    uri_suffix = manifest["id"].split(manifest_uri_prefix)[-1]
    extension_uri_suffix = manifest["extension_uri"].split(f"{rad_uri_prefix}extensions/")[-1]

    assert uri_suffix == extension_uri_suffix


def test_manifest_tag_uris(manifest):
    """
    Check that no tags are repeated in the manifest
    """

    tag_uri = {entry["tag_uri"] for entry in manifest["tags"]}
    assert len(tag_uri) == len(manifest["tags"]), "Duplicate tags found in the manifest"


def test_manifest_schema_uris(manifest):
    """
    Check that no schema uris are repeated in the manifest
    """
    schema_uris = {entry["schema_uri"] for entry in manifest["tags"]}
    assert len(schema_uris) == len(manifest["tags"]), "Duplicate schema URIs found in the manifest"


def test_manifest_consistency(manifest_uri, manifest_by_schema, manifest_by_tag):
    """
    Check that if a schema or tag is in a manifest and repeated in another
    manifest, that the schema and tag are the same.
    """
    # sanity check
    assert manifest_uri in manifest_by_schema
    assert manifest_uri in manifest_by_tag

    # Check each map in the current manifest against the other maps
    for schema_uri, tag_uri in manifest_by_schema[manifest_uri].items():
        for (manifest_uri, schema_map), tag_map in zip(manifest_by_schema.items(), manifest_by_tag.values(), strict=True):
            if schema_uri in schema_map:
                assert tag_uri in tag_map, (
                    f"Manifest {manifest_uri} has schema {schema_uri} but no tag {tag_uri} as unlike manifest {manifest_uri}, which does"
                )
                assert tag_uri == schema_map[schema_uri], (
                    f"Manifest {manifest_uri} maps schema {schema_uri} to tag {schema_map[schema_uri]} unlike manifest {manifest_uri}, which maps it to {tag_uri}"
                )

            if tag_uri in tag_map:
                assert schema_uri in schema_map, (
                    f"Manifest {manifest_uri} has tag {tag_uri} but no schema {schema_uri} as unlike manifest {manifest_uri}, which does"
                )
                assert schema_uri == tag_map[tag_uri], (
                    f"Manifest {manifest_uri} maps tag {tag_uri} to schema {tag_map[tag_uri]} unlike manifest {manifest_uri}, which maps it to {schema_uri}"
                )


def test_manifest_entries(manifest_entry, schema_uri_prefix, tag_uri_prefix):
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
    assert manifest_entry["tag_uri"].startswith(tag_uri_prefix)
    uri_suffix = manifest_entry["tag_uri"].split(tag_uri_prefix)[-1]
    # Remove tagged scalars from the uri string
    schema_uri = manifest_entry["schema_uri"]
    if "tagged_scalars" in schema_uri.split("/"):
        schema_uri = schema_uri.replace("tagged_scalars/", "")
    assert schema_uri.endswith(uri_suffix)
    assert schema_uri.startswith(schema_uri_prefix)


def test_no_lost_tags(latest_schema_tag_prefixes, latest_static_tags, previous_datamodels_tag):
    """
    Check that all tags in the previous datamodels manifest are present in the current tags
    """
    if previous_datamodels_tag.split("-")[0] not in latest_schema_tag_prefixes:
        assert previous_datamodels_tag in latest_static_tags, (
            f"Tag: {previous_datamodels_tag} is missing from the latest tags and is not static."
        )
