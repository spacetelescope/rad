"""
Test that the latest schemas are up to date and properly linked into rest of the schemas.
"""

import importlib.resources as importlib_resources
import json
import re
from importlib.metadata import Distribution

import pytest
import yaml

from rad import resources

from .conftest import LATEST_PATHS

DIRECT_URL = json.loads(Distribution.from_name("rad").read_text("direct_url.json"))
# Needs to be a bit complicated because tox still creates a wheel, it just does it a bit differently
# to preserve editable installs
IS_EDITABLE = DIRECT_URL["dir_info"].get("editable", False) if "dir_info" in DIRECT_URL else "editable" in DIRECT_URL["url"]


def test_smoke_latest_paths():
    """
    Smoke test to make sure that the latest paths are not empty.
    """
    assert LATEST_PATHS


def test_latest_filename(latest_path):
    """
    Check that the file name of the schema matches the schema ID WITHOUT the version number suffix.
    """
    # Check that the file name does not contain a version number
    assert len(str(latest_path).split("/rad/resources/")[-1].split("-")) == 1

    # Check that the file name is consistent with the schema ID
    uri = yaml.safe_load(latest_path.read_bytes())["id"]
    uri = uri.split("/schemas/")[-1] if "/schemas/" in uri else uri.split("/manifests/")[-1]
    assert uri.split("-")[0] == str(latest_path.parent / latest_path.stem).split("/latest/")[-1].split("-")[0]


@pytest.mark.skipif(not IS_EDITABLE, reason="Symbolic links are resolved in non-editable installs")
def test_latest_symlink(latest_path):
    """
    Check that each "latest" file has a simlink in the `schemas` or `manifests` directory
    that points to that file which includes its version number (e.g. matches its ID).
    """
    path_suffix = yaml.safe_load(latest_path.read_bytes())["id"].split("/roman/")[-1]
    path_prefix = importlib_resources.files(resources)
    symlink_path = path_prefix / f"{path_suffix}.yaml"

    # Check that the symlink both exists and is a symlink
    assert symlink_path.exists(), f"Expected symlink {symlink_path} to exist, but it does not."
    assert symlink_path.is_symlink(), f"Expected {symlink_path} to be a symlink, but it is not."

    # Check that the symlink is a relative symlink (absolute symlinks will break
    # on systems other than the one they were created on)
    assert not symlink_path.readlink().is_absolute(), f"Expected {symlink_path} to be a relative symlink, but it is not."

    # Check that the symlink points to the correct file
    assert symlink_path.resolve() == latest_path, f"Expected {symlink_path} to point to {latest_path}, but it does not."


def test_latest_schemas(latest_schema_tags, latest_schemas, latest_uri):
    """
    Check that the latest schemas are using the latest versions of the schema and tag uris.
    """
    # Sanity check that the latest_uri matches the id in the latest_schemas
    assert yaml.safe_load(latest_schemas[latest_uri])["id"] == latest_uri

    # Substitute all matching patterns with the latest_uri and check equality
    # If any substitution changes the schema, then we have a URI mismatch
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
        # If any substitution changes the schema, then we have a URI mismatch
        base_tag_uri = tag_uri.split("-")[0]
        base_tag_uri_regex = rf"{base_tag_uri}-\d+\.\d+\.\d+"
        for schema_uri, schema in latest_schemas.items():
            assert schema == re.sub(base_tag_uri_regex, tag_uri, schema), (
                f"Schema {schema_uri} has references to {tag_uri} that have not been updated!"
            )
