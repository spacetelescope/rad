"""
Test that the latest schemas are up to date and properly linked into rest of the schemas.
"""

import importlib.resources as importlib_resources
import re

import yaml

from rad import resources


def test_latest_filename(latest_path):
    """
    Check that the file name of the schema matches the schema ID WITHOUT the version number suffix.
    """
    # Check that the file name does not contain a version number
    assert len(str(latest_path).split("-")) == 1

    # Check that the file name is consistent with the schema ID
    uri = yaml.safe_load(latest_path.read_bytes())["id"]
    uri = uri.split("/schemas/")[-1] if "/schemas/" in uri else uri.split("/manifests/")[-1]
    assert uri.split("-")[0] == str(latest_path.parent / latest_path.stem).split("/latest/")[-1].split("-")[0]


def test_latest_symlink(latest_path):
    """
    Check that each "latest" file has a simlink in the `schemas` or `manifests` directory
    that points to that file which includes its version number (e.g. matches its ID).
    """
    path_suffix = yaml.safe_load(latest_path.read_bytes())["id"].split("/roman/")[-1]
    path_prefix = importlib_resources.files(resources)
    symlink_path = path_prefix / f"{path_suffix}.yaml"

    assert symlink_path.exists()
    assert symlink_path.is_symlink()


def test_latest_schemas(latest_schema_tags, latest_schemas, latest_uri):
    """
    Check that the latest schemas are using the latest versions of the schema and tag uris.
    """
    # Sanity check that the latest_uri matches the id in the latest_schemas
    assert yaml.safe_load(latest_schemas[latest_uri])["id"] == latest_uri

    # Substitute all matching patterns with the latest_uri and check equality
    # IF any substitution changes the schema, then we have a URI mismatch
    base_schema_uri = latest_uri.split("-")[0]
    base_schema_uri_regex = rf"{base_schema_uri}-\d+\.\d+\.\d+"
    for schema_uri, schema in latest_schemas.items():
        assert schema == re.sub(base_schema_uri_regex, latest_uri, schema), (
            f"Schema {schema_uri} has references to {latest_uri} that have not been updated!"
        )

    # Check that if the schema is tagged in the manifest that its tag version is the same as the schema version
    if latest_uri in latest_schema_tags:
        tag_uri = latest_schema_tags[latest_uri]
        tag_version = tag_uri.split("-")[-1]
        schema_version = latest_uri.split("-")[-1]
        assert tag_version == schema_version

        # Substitute all matching patterns with the latest_uri and check equality
        # IF any substitution changes the schema, then we have a URI mismatch
        base_tag_uri = tag_uri.split("-")[0]
        base_tag_uri_regex = rf"{base_tag_uri}-\d+\.\d+\.\d+"
        for schema_uri, schema in latest_schemas.items():
            assert schema == re.sub(base_tag_uri_regex, tag_uri, schema), (
                f"Schema {schema_uri} has references to {tag_uri} that have not been updated!"
            )
