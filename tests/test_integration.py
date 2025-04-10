"""
Test that the asdf library integration is working properly.
"""

import importlib.resources as importlib_resources
from pathlib import Path

import asdf
import pytest
import yaml
from semantic_version import Version

from rad import resources


@pytest.mark.parametrize("manifest_path", (importlib_resources.files(resources) / "manifests").glob("**/*.yaml"))
def test_manifest_integration(manifest_path):
    content = manifest_path.read_bytes()
    manifest = yaml.safe_load(content)
    asdf_content = asdf.get_config().resource_manager[manifest["id"]]
    assert asdf_content == content


def test_schema_integration(schema_path):
    content = schema_path.read_bytes()
    schema = yaml.safe_load(content)
    asdf_content = asdf.get_config().resource_manager[schema["id"]]
    assert asdf_content == content


def test_schema_filename(schema_path):
    """
    Check the filename pattern aligns with the schema ID.
    """
    prefix = importlib_resources.files(resources)
    id_suffix = str(schema_path.with_suffix("")).split(str(prefix))[-1]

    schema = yaml.safe_load(schema_path.read_bytes())
    if "schemas" in str(schema_path) or "manifests" in str(schema_path):
        assert schema["id"].endswith(id_suffix)

        if "schemas" in str(schema_path):
            # check that there is a latest version of the schema
            latest_path = (
                Path(str(schema_path).split("schemas")[0]) / "latest" / f"{id_suffix.split('/schemas')[1][1:].split('-')[0]}.yaml"
            )
            assert latest_path.exists(), latest_path
            latest = yaml.safe_load(latest_path.read_bytes())

            # Check that the version number is lower than the latest version
            assert Version(schema["id"].split("-")[1]) < Version(latest["id"].split("-")[1])
    else:
        # latest schemas case -> filename "../latest/.." should instead be "../schemas/.."
        # and the version number should be missing
        suffix = "/".join(id_suffix.split("/")[2:])
        id_suffix = f"/schemas/{suffix}"
        assert schema["id"].split("-")[0].endswith(id_suffix)

        # There should not be a schemas file with the exact version number used
        # by latest
        assert not (prefix / f"{id_suffix}-{schema['id'].split('-')[1]}.yaml").exists()
