from dataclasses import is_dataclass

import pytest

from rad.reader._basic import Basic
from rad.reader._errors import UnreadableDataError
from rad.reader._link import Ref
from rad.reader._reader import KeyWords
from rad.reader._schema import AllOf, AnyOf, Not, OneOf, Schema
from rad.reader._type import Null, Numeric, Object, String


class TestSchema:
    def test_keywords(self):
        """
        Test that the Schema schema has the correct keywords.
        """

        assert Schema.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
        }
        assert issubclass(Schema.KeyWords, KeyWords)

    def test_extract_definitions(self, basic_data, definitions_data):
        schema = Schema.extract({**basic_data, **definitions_data})

        assert isinstance(schema, Basic)
        assert isinstance(schema, Schema)
        assert is_dataclass(schema)

        assert isinstance(schema.definitions, dict)
        assert schema.definitions
        assert len(schema.definitions) == 3

        assert "test_string" in schema.definitions
        string = schema.definitions["test_string"]
        assert isinstance(string, String)

        assert "test_number" in schema.definitions
        number = schema.definitions["test_number"]
        assert isinstance(number, Numeric)

        assert "test_object" in schema.definitions
        object_ = schema.definitions["test_object"]
        assert isinstance(object_, Object)

    def test_extract_ref_definitions(self, basic_data, definitions_ref_data):
        schema = Schema.extract({**basic_data, **definitions_ref_data})

        assert isinstance(schema, Schema)

        assert isinstance(schema.definitions, Ref)
        assert schema.definitions.ref == "http://example.com/ref_schema"

    def test_extract_bad_definitons(self, basic_data):
        with pytest.raises(UnreadableDataError, match=r"Expected 'definitions' to be a Mapping or a \$ref, got.*"):
            Schema.extract({**basic_data, **{"definitions": "invalid"}})

    def test_extract_enum(self, basic_data, enum_data):
        schema = Schema.extract({**basic_data, **enum_data})

        assert isinstance(schema, Schema)

        assert isinstance(schema.enum, list)
        assert schema.enum
        assert len(schema.enum) == 3
        assert schema.enum == ["value1", "value2", "value3"]


class TestAllOf:
    def test_keywords(self):
        """
        Test that the AllOf schema has the correct keywords.
        """

        assert AllOf.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "ALL_OF": "allOf",
        }
        assert issubclass(AllOf.KeyWords, KeyWords)

    def test_extract(self, basic_data, all_of_data):
        schema = Schema.extract({**basic_data, **all_of_data})

        assert isinstance(schema, Schema)
        assert isinstance(schema, AllOf)
        assert is_dataclass(schema)

        assert isinstance(schema.all_of, list)
        assert schema.all_of
        assert len(schema.all_of) == 2

        for item in schema.all_of:
            assert isinstance(item, Object)

    def test_archive_data_full(self, manager, basic_data, all_of_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        schema = Schema.extract({**basic_data, **all_of_data, "archive_catalog": archive_catalog_data})
        # Note that the archive cannot handle archive data within the pattern properties
        assert schema.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "description": "Test Description",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
            "properties": [
                {
                    "name": "property1",
                    "title": "Test Title",
                    "description": "Test Description",
                    "archive_meta": "Test Archive Meta",
                    "datatype": "Test DataType",
                    "destination": ["destination1", "destination2"],
                },
                {
                    "name": "property2",
                    "title": "Test Title",
                    "description": "Test Description",
                    "archive_meta": "Test Archive Meta",
                    "datatype": "Test DataType",
                    "destination": ["destination1", "destination2"],
                },
            ],
        }

    def test_archive_data_merge_properties(self, manager):
        """
        Test the merging of objects with all_of for properties
        """
        data = {
            "title": "Test Title",
            "description": "Test Description",
            "allOf": [
                {
                    "title": "allOf Title 1",
                    "type": "object",
                    "properties": {
                        "property1": {
                            "type": "string",
                            "title": "property 1",
                            "archive_catalog": {
                                "datatype": "p1",
                                "destination": ["p1_dest_1", "p1_dest_2"],
                            },
                        },
                        "property2": {
                            "type": "number",
                            "title": "property 2",
                            "archive_catalog": {"datatype": "p2", "destination": ["p2_dest_1", "p2_dest_2"]},
                        },
                    },
                },
                {
                    "title": "allOf Title 2",
                    "type": "object",
                    "properties": {
                        "property1": {
                            "type": "string",
                            "title": "property 1 other",
                            "description": "This is property 1",
                            "archive_catalog": {
                                "datatype": "p1",
                                "destination": ["p1_dest_3", "p1_dest_4"],
                            },
                        },
                        "property3": {
                            "type": "number",
                            "title": "property 3",
                            "archive_catalog": {"datatype": "p3", "destination": ["p3_dest_1", "p3_dest_2"]},
                        },
                    },
                },
            ],
        }

        schema = Schema.extract(data)
        assert schema.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "description": "Test Description",
            "properties": [
                {
                    "name": "property1",
                    "title": "property 1",
                    "description": "This is property 1",
                    "datatype": "p1",
                    "destination": ["p1_dest_1", "p1_dest_2", "p1_dest_3", "p1_dest_4"],
                },
                {
                    "name": "property2",
                    "title": "property 2",
                    "datatype": "p2",
                    "destination": ["p2_dest_1", "p2_dest_2"],
                },
                {
                    "name": "property3",
                    "title": "property 3",
                    "datatype": "p3",
                    "destination": ["p3_dest_1", "p3_dest_2"],
                },
            ],
        }

    def test_archive_data_empty(self, manager):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        all_of_data = [
            {
                "type": "object",
                "properties": {
                    "property1": {
                        "type": "string",
                    },
                    "property2": {
                        "type": "number",
                    },
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
        ]

        schema = Schema.extract({"allOf": all_of_data})
        # Note that the archive cannot handle archive data within the pattern properties
        assert schema.archive_data("test_name", manager) is None


class TestAnyOf:
    def test_keywords(self):
        """
        Test that the AnyOf schema has the correct keywords.
        """

        assert AnyOf.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "ANY_OF": "anyOf",
        }
        assert issubclass(AnyOf.KeyWords, KeyWords)

    def test_extract(self, basic_data, any_of_data):
        schema = Schema.extract({**basic_data, **any_of_data})

        assert isinstance(schema, Schema)
        assert isinstance(schema, AnyOf)

        assert isinstance(schema.any_of, list)
        assert schema.any_of
        assert len(schema.any_of) == 2

        for item in schema.any_of:
            assert isinstance(item, String | Null)

    def test_archive_data_full(self, manager, basic_data, any_of_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        schema = Schema.extract({**basic_data, **any_of_data, "archive_catalog": archive_catalog_data})
        # Note that the archive cannot handle archive data within the pattern properties
        assert schema.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "description": "Test Description",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
            "anyOf": [
                {
                    "name": "test_name_0",
                    "title": "Test Title",
                    "description": "Test Description",
                    "archive_meta": "Test Archive Meta",
                    "datatype": "Test DataType",
                    "destination": ["destination1", "destination2"],
                },
                {
                    "name": "test_name_1",
                    "title": "Test Title",
                    "description": "Test Description",
                    "archive_meta": "Test Archive Meta",
                    "datatype": "Test DataType",
                    "destination": ["destination1", "destination2"],
                },
            ],
        }

    def test_archive_data_empty(self, manager):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        any_of_data = [
            {
                "type": "object",
                "properties": {
                    "property1": {
                        "type": "string",
                    },
                    "property2": {
                        "type": "number",
                    },
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
        ]

        schema = Schema.extract({"anyOf": any_of_data})
        # Note that the archive cannot handle archive data within the pattern properties
        assert schema.archive_data("test_name", manager) is None


class TestNot:
    def test_keywords(self):
        """
        Test that the Not schema has the correct keywords.
        """

        assert Not.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "NOT_": "not",
        }
        assert issubclass(Not.KeyWords, KeyWords)

    def test_extract(self, basic_data, not_data):
        schema = Schema.extract({**basic_data, **not_data})

        assert isinstance(schema, Schema)
        assert isinstance(schema, Not)
        assert is_dataclass(schema)

        assert isinstance(schema.not_, Object)

    def test_archive_data_full(self, manager, basic_data, not_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        schema = Schema.extract({**basic_data, **not_data, "archive_catalog": archive_catalog_data})
        # Note that the archive cannot handle archive data within the pattern properties
        import pprint

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(schema.archive_data("test_name", manager))
        assert schema.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "description": "Test Description",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
            "not": {
                "name": "test_name_not",
                "title": "Test Title",
                "description": "Test Description",
                "archive_meta": "Test Archive Meta",
                "datatype": "Test DataType",
                "destination": ["destination1", "destination2"],
                "properties": [
                    {
                        "name": "property1",
                        "title": "Test Title",
                        "description": "Test Description",
                        "archive_meta": "Test Archive Meta",
                        "datatype": "Test DataType",
                        "destination": ["destination1", "destination2"],
                    },
                    {
                        "name": "property2",
                        "title": "Test Title",
                        "description": "Test Description",
                        "archive_meta": "Test Archive Meta",
                        "datatype": "Test DataType",
                        "destination": ["destination1", "destination2"],
                    },
                ],
            },
        }


class TestOneOf:
    def test_keywords(self):
        """
        Test that the OneOf schema has the correct keywords.
        """

        assert OneOf.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "ONE_OF": "oneOf",
        }
        assert issubclass(OneOf.KeyWords, KeyWords)

    def test_extract(self, basic_data, one_of_data):
        schema = Schema.extract({**basic_data, **one_of_data})

        assert isinstance(schema, Schema)
        assert isinstance(schema, OneOf)
        assert is_dataclass(schema)

        assert isinstance(schema.one_of, list)
        assert schema.one_of
        assert len(schema.one_of) == 2

        for item in schema.one_of:
            assert isinstance(item, String | Numeric)

    def test_archive_data_full(self, manager, basic_data, one_of_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        schema = Schema.extract({**basic_data, **one_of_data, "archive_catalog": archive_catalog_data})
        # Note that the archive cannot handle archive data within the pattern properties
        assert schema.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "description": "Test Description",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
            "oneOf": [
                {
                    "name": "test_name_0",
                    "title": "Test Title",
                    "description": "Test Description",
                    "archive_meta": "Test Archive Meta",
                    "datatype": "Test DataType",
                    "destination": ["destination1", "destination2"],
                },
                {
                    "name": "test_name_1",
                    "title": "Test Title",
                    "description": "Test Description",
                    "archive_meta": "Test Archive Meta",
                    "datatype": "Test DataType",
                    "destination": ["destination1", "destination2"],
                },
            ],
        }

    def test_archive_data_empty(self, manager):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        one_of_data = [
            {
                "type": "object",
                "properties": {
                    "property1": {
                        "type": "string",
                    },
                    "property2": {
                        "type": "number",
                    },
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
        ]

        schema = Schema.extract({"oneOf": one_of_data})
        # Note that the archive cannot handle archive data within the pattern properties
        assert schema.archive_data("test_name", manager) is None
