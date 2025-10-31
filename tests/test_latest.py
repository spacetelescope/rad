"""
Test that the latest schemas are up to date and properly linked into rest of the schemas.
"""

import importlib.resources as importlib_resources
import json
import re
from collections.abc import Mapping
from importlib.metadata import Distribution

import asdf.treeutil
import pytest
import yaml

from rad import resources
from rad._parser import archive_schema, super_schema

DIRECT_URL = json.loads(Distribution.from_name("rad").read_text("direct_url.json"))
# Needs to be a bit complicated because tox still creates a wheel, it just does it a bit differently
# to preserve editable installs
IS_EDITABLE = DIRECT_URL["dir_info"].get("editable", False) if "dir_info" in DIRECT_URL else "editable" in DIRECT_URL["url"]


class TestLastestResources:
    def test_smoke_latest_paths(self, latest_paths):
        """
        Smoke test to make sure that the latest paths are not empty.
        """
        assert latest_paths

    def test_latest_filename(self, latest_path):
        """
        Check that the file name of the schema matches the schema ID WITHOUT the version number suffix.
        """
        # Check that the file name does not contain a version number
        assert len(str(latest_path).split("/rad/latest/")[-1].split("-")) == 1

        # Check that the file name is consistent with the schema ID
        uri = yaml.safe_load(latest_path.read_bytes())["id"]
        uri = uri.split("/schemas/")[-1] if "/schemas/" in uri else uri.split("/manifests/")[-1]

        # Find the filename without the version number suffix
        filename = str(latest_path.parent / latest_path.stem).split("/latest/")[-1].split("-")[0]

        # Note that the manifests are nested in the manifests directory
        assert uri.split("-")[0] == filename.split("manifests/")[-1] if "manifests/" in filename else filename

    @pytest.mark.skipif(not IS_EDITABLE, reason="Symbolic links are resolved in non-editable installs")
    def test_latest_symlink(self, latest_path):
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

    def test_latest_datamodels_not_static(self, latest_datamodels_tag_uri, latest_static_tags):
        """
        Check that the latest datamodels entry is not static.
        """
        assert latest_datamodels_tag_uri not in latest_static_tags, (
            f"Tag: {latest_datamodels_tag_uri} is listed as static, so it should not be the latest datamodels manifest."
        )

    def test_latest_static_tags_previous_existence(self, latest_static_tag_uri, datamodel_tag_uris):
        """
        Check that if a static tag exists in latest then, it must have existed in some previous version's
        datamodels.

        Note
        ----
        The previous test shows that the latest datamodel manifest does not have the static tag and
        datamodel_tag_uris only sources tags from the datamodels manifest, so this is testing that the static
        tag must have existed in some datamodels manifest.
        """
        assert latest_static_tag_uri in datamodel_tag_uris, (
            f"Tag: {latest_static_tag_uri} does not exist in any previous version's datamodels."
        )

    def test_latest_datamodels_only_reference_latest(self, latest_datamodels_tag_uri, latest_uris, tag_schema_map):
        """
        Check that the latest datamodels manifest only references schemas within latest.
        """
        assert tag_schema_map[latest_datamodels_tag_uri] in latest_uris, (
            f"{tag_schema_map[latest_datamodels_tag_uri]} is not in latest uris."
        )

    def test_latest_schemas(self, latest_schema_tags, latest_schemas, latest_uri):
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

    def test_no_internal_tags(self, latest_tagged_schema_uri, current_resources):
        """
        Check that tagged entries in the latest manifest are all datamodels and not internal schemas.
        """

        assert "datamodel_name" in current_resources[latest_tagged_schema_uri], (
            f"{latest_tagged_schema_uri} is tagged but not a datamodel."
        )

    def test_tagged_schema_path(
        self, latest_tagged_schema_uri, latest_dir, latest_reference_files_dir, latest_ccsp_dir, latest_uri_paths
    ):
        """
        Check that all datamodels are in the top-level directory and all reference files are in the reference_files directory.
        """
        path = latest_uri_paths[latest_tagged_schema_uri]
        if "reference_file" in latest_tagged_schema_uri:
            assert path.parent == latest_reference_files_dir, (
                f"{latest_tagged_schema_uri} is a reference file that is not in the reference_files directory."
            )
        elif "CCSP" in latest_tagged_schema_uri:
            assert path.parent.parent == latest_ccsp_dir, (
                f"{latest_tagged_schema_uri} is a CCSP file that is not in the CCSP directory."
            )
            ccsp_id_dir = path.parent.name
            ccsp_id_prefix = latest_tagged_schema_uri.split("/")[-1].split("_")[0]
            assert ccsp_id_prefix.upper() == ccsp_id_dir, (
                f"{latest_tagged_schema_uri} is not prefixed with '{ccsp_id_dir.lower()}_'"
            )
        else:
            assert path.parent == latest_dir, f"{latest_tagged_schema_uri} is a datamodel that is not in the top-level directory."

    def test_top_level_schema(self, latest_top_level_path, metaschema_uri, latest_paths):
        """
        Check that a schema located directly under the `latest` directory are datamodels (or the single metaschema).
        """
        schema = latest_paths[latest_top_level_path]

        if schema["id"] != metaschema_uri:
            assert "datamodel_name" in schema, f"{schema['id']} is a top level schema but not a datamodel."

    @pytest.mark.usefixtures("asdf_ssc_config")
    def test_super_schema(self, latest_uri, metaschema_uri):
        """
        Check that the super_schema function can process all latest schemas without error.
        """
        if latest_uri == metaschema_uri:
            pytest.skip("Skipping metaschema as have no need to super schema it.")

        schema = super_schema(latest_uri)  # smoke out if a schema does not parse

        def callback(node):
            if isinstance(node, Mapping):
                assert "allOf" not in node, f"Schema {latest_uri} still has an allOf that was not resolved!"
                assert "$ref" not in node, f"Schema {latest_uri} still has a $ref that was not resolved!"

        asdf.treeutil.walk(schema, callback)

    @pytest.mark.usefixtures("asdf_ssc_config")
    def test_archive_schema(self, latest_archive_uri):
        """
        Check that the super_schema function can process all latest archive schemas without error.
        """
        schema = super_schema(latest_archive_uri)  # smoke out if a schema does not parse
        archive = archive_schema(schema)

        def callback(node):
            if isinstance(node, Mapping):
                if "properties" in node or "archive_meta" in node:
                    for key in node:
                        if key not in ("properties", "archive_meta"):
                            raise ValueError(f"Schema {latest_archive_uri} has non-archive property {key} in archive schema!")
                elif "archive_catalog" in node:
                    assert len(node) == 1, f"Schema {latest_archive_uri} has non-archive keywords in archive schema!"

                    assert {"datatype", "destination"} == set(node["archive_catalog"]), (
                        f"Schema {latest_archive_uri} has unexpected keywords in archive_catalog!"
                    )

        asdf.treeutil.walk(archive, callback)
