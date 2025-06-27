from types import MappingProxyType

import pytest

from rad.reader._manager import Manager


@pytest.fixture()
def manager() -> Manager:
    """
    Fixture to provide a Manager instance for tests.
    This can be used to manage schemas and their addresses.
    """
    return Manager()


@pytest.fixture(scope="session")
def root_data() -> MappingProxyType[str, str]:
    """
    Fixture to provide a root data structure for tests.
    """
    return MappingProxyType(
        {
            "id": "test_id",
            "$schema": "http://example.com/schema",
        }
    )


@pytest.fixture(scope="session")
def metadata_data() -> MappingProxyType[str, str]:
    """
    Fixture to provide metadata data structure for tests.
    """
    return MappingProxyType(
        {
            "title": "Test Title",
            "description": "Test Description",
            "default": "Test Default",
        }
    )


@pytest.fixture(scope="session")
def archive_catalog_data() -> MappingProxyType[str, str]:
    """
    Fixture to provide archive catalog data structure for tests.
    """
    return MappingProxyType(
        {
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }
    )


@pytest.fixture(scope="session")
def rad_data() -> MappingProxyType[str, str]:
    """
    Fixture to provide RAD data structure for tests.
    """
    return MappingProxyType(
        {
            "unit": "Test Unit",
            "datamodel_name": "Test DataModel Name",
            "archive_meta": "Test Archive Meta",
        }
    )


@pytest.fixture(scope="session")
def basic_data(root_data, metadata_data, rad_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide a basic data structure for tests.
    Combines root and metadata data.
    """
    return MappingProxyType(
        {
            **root_data,
            **metadata_data,
            **rad_data,
        }
    )


@pytest.fixture(scope="session")
def string_data(basic_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide string data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "string",
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def number_data(basic_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide numeric data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "number",
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def single_item_array_data(basic_data, string_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide array data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "array",
            "items": string_data,
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def multi_item_array_data(basic_data, string_data, number_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide array data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "array",
            "items": [
                string_data,
                number_data,
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def boolean_data(basic_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide boolean data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "boolean",
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def integer_data(basic_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide integer data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "integer",
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def null_data(basic_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide null data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "null",
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def object_data(basic_data, archive_catalog_data, string_data, number_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide object data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "object",
            "properties": {
                "property1": string_data,
                "property2": number_data,
            },
            "required": ["property1"],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def pattern_object_data(basic_data, archive_catalog_data, string_data, number_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide pattern object data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "object",
            "patternProperties": {
                r"^pattern_.*": string_data,
                r"^pattern_property2$": number_data,
            },
            "additionalProperties": False,
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def all_of_data(basic_data, archive_catalog_data, string_data, number_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide allOf data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "property1": string_data,
                        "property2": number_data,
                    },
                    "required": ["property1"],
                },
                {
                    "type": "object",
                    "patternProperties": {
                        r"^pattern_.*": {
                            "type": "string",
                        },
                        r"^pattern_property2$": {
                            "type": "number",
                        },
                    },
                    "additionalProperties": False,
                },
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def all_of_object_object_data(basic_data, archive_catalog_data, object_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide allOf data structure for tests with object types.
    """
    return MappingProxyType(
        {
            **basic_data,
            "allOf": [
                object_data,
                {
                    "type": "object",
                    "properties": {
                        "property3": {
                            "type": "string",
                        },
                    },
                    "required": ["property3"],
                },
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def all_of_array_data(
    basic_data, archive_catalog_data, single_item_array_data, multi_item_array_data
) -> MappingProxyType[str, str]:
    return MappingProxyType(
        {
            **basic_data,
            "allOf": [
                single_item_array_data,
                multi_item_array_data,
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def any_of_data(basic_data, archive_catalog_data, string_data, null_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide anyOf data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "anyOf": [
                string_data,
                null_data,
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def not_data(basic_data, archive_catalog_data, object_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide not data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "not": object_data,
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def one_of_data(basic_data, archive_catalog_data, string_data, number_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide oneOf data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "oneOf": [
                string_data,
                number_data,
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def ref_data() -> MappingProxyType[str, str]:
    """
    Fixture to provide $ref data structure for tests.
    """
    return MappingProxyType(
        {
            "$ref": "http://example.com/ref_schema",
        },
    )


@pytest.fixture(scope="session")
def top_ref_data(basic_data, archive_catalog_data, ref_data) -> MappingProxyType[str, str]:
    """
    Fixture providing a top-level $ref data structure for tests.
    """

    return MappingProxyType(
        {
            **basic_data,
            "allOf": [
                ref_data,
            ],
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def tag_data(basic_data, archive_catalog_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide tag data structure for tests.
    """
    return MappingProxyType(
        {
            **basic_data,
            "type": "object",
            "properties": {
                "property1": {
                    "tag": "asdf://test.com/tags/test_tag1",
                },
                "property2": {
                    "tag": "asdf://test.com/tags/test_tag2",
                },
            },
            "archive_catalog": archive_catalog_data,
        }
    )


@pytest.fixture(scope="session")
def definitions_data(string_data, number_data, object_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide definitions data structure for tests.
    """
    return MappingProxyType(
        {
            "definitions": {
                "test_string": string_data,
                "test_number": number_data,
                "test_object": object_data,
            },
        }
    )


@pytest.fixture(scope="session")
def definitions_ref_data(ref_data) -> MappingProxyType[str, str]:
    """
    Fixture to provide definitions with $ref data structure for tests.
    """
    return MappingProxyType(
        {
            "definitions": {
                **ref_data,
            },
        }
    )


@pytest.fixture(scope="session")
def enum_data() -> MappingProxyType[str, str]:
    """
    Fixture to provide enum data structure for tests.
    """
    return MappingProxyType(
        {
            "enum": ["value1", "value2", "value3"],
        }
    )
