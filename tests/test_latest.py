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
        assert len(str(latest_path).split("/rad/resources/")[-1].split("-")) == 1

        # Check that the file name is consistent with the schema ID
        uri = yaml.safe_load(latest_path.read_bytes())["id"]
        uri = uri.split("/schemas/")[-1] if "/schemas/" in uri else uri.split("/manifests/")[-1]
        assert uri.split("-")[0] == str(latest_path.parent / latest_path.stem).split("/latest/")[-1].split("-")[0]

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


@pytest.fixture(scope="module")
def manager():
    """
    Fixture to create a Manager instance for testing.
    """
    from rad.reader._manager import Manager

    return Manager.from_rad()


class TestRadReader:
    def test_schema(self, manager, current_resources, schema_uri_prefix, latest_uri):
        """
        Test that the schema information from a schema can be extracted correctly.
        """
        from rad.reader._link import Ref, Tag
        from rad.reader._schema import AllOf, AnyOf, Not, OneOf, Schema
        from rad.reader._type import Array, Boolean, Null, Numeric, Object, String, Type

        def check_basic(extract, schema):
            assert extract.id == schema.get("id")
            assert extract.schema == schema.get("$schema")

            assert extract.title == schema.get("title")
            assert extract.description == schema.get("description")
            assert extract.default == schema.get("default")

            assert extract.unit == schema.get("unit")
            assert extract.datamodel_name == schema.get("datamodel_name")
            assert extract.archive_meta == schema.get("archive_meta")

            if extract.archive_catalog is None:
                assert schema.get("archive_catalog") is None
            else:
                assert extract.archive_catalog.datatype == schema["archive_catalog"]["datatype"]
                assert extract.archive_catalog.destination == schema["archive_catalog"]["destination"]

        def check_array(schema, extract):
            check_basic(extract, schema)
            assert extract.type == schema["type"]

            assert extract.additional_items is schema.get("additionalItems")
            assert extract.min_items == schema.get("minItems")
            assert extract.max_items == schema.get("maxItems")
            assert extract.unique_items == schema.get("uniqueItems")

            if extract.items is None:
                assert schema.get("items") is None
            else:
                assert schema.get("items") is not None

                if isinstance(schema["items"], list):
                    for schema_item, extract_item in zip(schema["items"], extract.items, strict=True):
                        check_schema(schema_item, extract_item)
                elif isinstance(schema["items"], dict):
                    assert len(extract.items) == 1
                    check_schema(schema["items"], extract.items[0])

        def check_numeric(schema, extract):
            check_basic(extract, schema)
            assert extract.type == schema["type"]

            assert extract.minimum == schema.get("minimum")
            assert extract.maximum == schema.get("maximum")
            assert extract.exclusive_minimum == schema.get("exclusiveMinimum")
            assert extract.exclusive_maximum == schema.get("exclusiveMaximum")
            assert extract.multiple_of == schema.get("multipleOf")

        def check_object(schema, extract):
            check_basic(extract, schema)
            assert extract.type == schema["type"]

            assert extract.additional_properties == schema.get("additionalProperties")
            assert extract.max_properties == schema.get("maxProperties")
            assert extract.min_properties == schema.get("minProperties")
            assert extract.dependencies == schema.get("dependencies")

            assert extract.required == schema.get("required")

            if extract.properties is None:
                assert schema.get("properties") is None
            else:
                for (schema_key, schema_property), (extract_key, extract_property) in zip(
                    schema["properties"].items(), extract.properties.items(), strict=True
                ):
                    assert extract_key == schema_key
                    check_schema(schema_property, extract_property)

            if extract.pattern_properties is None:
                assert schema.get("patternProperties") is None
            else:
                for (schema_key, schema_property), (extract_key, extract_property) in zip(
                    schema["patternProperties"].items(), extract.pattern_properties.items(), strict=True
                ):
                    assert extract_key == schema_key
                    check_schema(schema_property, extract_property)

        def check_string(schema, extract):
            check_basic(extract, schema)
            assert extract.type == schema["type"]

            assert extract.pattern == schema.get("pattern")
            assert extract.min_length == schema.get("minLength")
            assert extract.max_length == schema.get("maxLength")

        def check_type(schema, extract):
            check_basic(extract, schema)

            match extract.type:
                case "array":
                    assert isinstance(extract, Array)

                    check_array(schema, extract)
                case "boolean":
                    assert isinstance(extract, Boolean)
                case "null":
                    assert isinstance(extract, Null)
                case "number" | "integer":
                    assert isinstance(extract, Numeric)
                    check_numeric(schema, extract)
                case "object":
                    assert isinstance(extract, Object)
                    check_object(schema, extract)
                case "string":
                    assert isinstance(extract, String)
                    check_string(schema, extract)
                case _:
                    raise TypeError(f"Unknown type: {extract.type}")

        def check_all_of(schema, extract):
            check_basic(extract, schema)

            for schema_item, extract_item in zip(schema["allOf"], extract.all_of, strict=True):
                check_schema(schema_item, extract_item)

        def check_any_of(schema, extract):
            check_basic(extract, schema)

            for schema_item, extract_item in zip(schema["anyOf"], extract.any_of, strict=True):
                check_schema(schema_item, extract_item)

        def check_not(schema, extract):
            check_basic(extract, schema)
            check_schema(schema["not"], extract.not_)

        def check_one_of(schema, extract):
            check_basic(extract, schema)

            for schema_item, extract_item in zip(schema["oneOf"], extract.one_of, strict=True):
                check_schema(schema_item, extract_item)

        def check_ref(schema, extract):
            check_basic(extract, schema)

            assert extract.ref == schema["$ref"]

        def check_tag(schema, extract):
            check_basic(extract, schema)

            assert extract.tag == schema["tag"]

        def check_schema(schema, extract):
            check_basic(extract, schema)
            assert isinstance(extract, Schema)

            if extract.definitions is None:
                assert schema.get("definitions") is None
            else:
                for (schema_key, schema_definition), (extract_key, extract_definition) in zip(
                    schema["definitions"].items(), extract.definitions.items(), strict=True
                ):
                    assert extract_key == schema_key
                    check_schema(schema_definition, extract_definition)

            if extract.enum is None:
                assert schema.get("enum") is None
            else:
                assert extract.enum == schema["enum"]

            if "type" in schema:
                assert isinstance(extract, Type)
                check_type(schema, extract)

            elif "allOf" in schema:
                assert isinstance(extract, AllOf)
                check_all_of(schema, extract)

            elif "anyOf" in schema:
                assert isinstance(extract, AnyOf)
                check_any_of(schema, extract)

            elif "not" in schema:
                assert isinstance(extract, Not)
                check_not(schema, extract)

            elif "oneOf" in schema:
                assert isinstance(extract, OneOf)
                check_one_of(schema, extract)

            elif "$ref" in schema:
                assert isinstance(extract, Ref)
                check_ref(schema, extract)

            elif "tag" in schema:
                assert isinstance(extract, Tag)
                check_tag(schema, extract)

            else:
                assert type(extract) is Schema
                assert "definitions" in schema, "Cannot identify the schema"

        if latest_uri.startswith(schema_uri_prefix):
            schema = current_resources[latest_uri]
            extract = manager[latest_uri]

            check_schema(schema, extract)

    def test_meta_uris(self, manager, archive_meta_uri):
        """
        Test that we can extract the archive information output from the archive_meta schemas
        --> This is a simple smoke test to ensure we can generate the expected output without
            code failures. This does not check the correctness of the output.
        """
        manager.archive_data(archive_meta_uri)
