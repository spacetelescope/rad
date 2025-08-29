from dataclasses import is_dataclass

import pytest

from rad.reader._basic import Basic
from rad.reader._errors import UnhandledKeyError, UnreadableDataError
from rad.reader._reader import KeyWords
from rad.reader._schema import Schema
from rad.reader._type import Array, Boolean, Null, Numeric, Object, String, Type


class TestType:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Type.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
        }
        assert issubclass(Type.KeyWords, KeyWords)

    def test_type_key_failure(self, basic_data):
        """
        Test that the Type schema cannot be extracted from a dictionary without a type.
        """
        with pytest.raises(UnhandledKeyError, match="Unhandled type value: .*"):
            Schema.extract({**basic_data, "type": "unsupported_type"})

    def test_extract_failure(self, basic_data):
        """
        Test that the Type schema cannot be extracted from a dictionary without a type.
        """
        with pytest.raises(UnreadableDataError, match="Missing 'type' key in data."):
            Type.extract(basic_data)


class TestArray:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Array.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "ITEMS": "items",
            "ADDITIONAL_ITEMS": "additionalItems",
            "MAX_ITEMS": "maxItems",
            "MIN_ITEMS": "minItems",
            "UNIQUE_ITEMS": "uniqueItems",
        }
        assert issubclass(Array.KeyWords, KeyWords)

    def test_single_item_extract(self, basic_data, single_item_array_data):
        """
        Test that the Type schema can be extracted from a dictionary.
        """
        array = Schema.extract({**basic_data, **single_item_array_data})
        assert isinstance(array, Type)
        assert isinstance(array, Array)
        assert is_dataclass(array)

        assert isinstance(array.items, list)
        assert len(array.items) == 1
        item = array.items[0]
        assert isinstance(item, String)
        assert item.type == "string"

        assert array.additional_items is None
        assert array.max_items is None
        assert array.min_items is None
        assert array.unique_items is None

    def test_multi_item_extract(self, basic_data, multi_item_array_data):
        """
        Test that the Type schema can be extracted from a dictionary.
        """
        array = Schema.extract({**basic_data, **multi_item_array_data})
        assert isinstance(array, Type)
        assert isinstance(array, Array)
        assert is_dataclass(array)

        assert isinstance(array.items, list)
        assert len(array.items) == 2

        assert isinstance(array.items[0], Type)
        assert isinstance(array.items[0], String)
        assert array.items[0].type == "string"

        assert isinstance(array.items[1], Type)
        assert isinstance(array.items[1], Numeric)
        assert array.items[1].type == "number"

        assert array.additional_items is None
        assert array.max_items is None
        assert array.min_items is None
        assert array.unique_items is None

    def test_extract_failure(self, basic_data):
        with pytest.raises(UnreadableDataError, match=r"Expected 'items' to be a list, dict, or Schema instance, got.*"):
            Schema.extract(
                data={
                    **basic_data,
                    "type": "array",
                    "items": Basic(
                        id="bar",
                        schema="baz",
                        title="Foo",
                        description="A foo item",
                        default=None,
                        archive_catalog=None,
                        unit=None,
                        datamodel_name=None,
                        archive_meta=None,
                    ),
                },
            )


class TestBoolean:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Boolean.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
        }
        assert issubclass(Boolean.KeyWords, KeyWords)

    def test_extract(self, basic_data, boolean_data):
        """
        Test that the Boolean schema can be extracted from a dictionary.
        """
        boolean = Schema.extract({**basic_data, **boolean_data})
        assert isinstance(boolean, Type)
        assert isinstance(boolean, Boolean)
        assert is_dataclass(boolean)
        assert boolean.type == "boolean"


class TestNumeric:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Numeric.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "MINIMUM": "minimum",
            "MAXIMUM": "maximum",
            "EXCLUSIVE_MINIMUM": "exclusiveMinimum",
            "EXCLUSIVE_MAXIMUM": "exclusiveMaximum",
            "MULTIPLE_OF": "multipleOf",
        }
        assert issubclass(Numeric.KeyWords, KeyWords)

    def test_extract_integer(self, basic_data, integer_data):
        """
        Test that the Numeric schema can be extracted from a dictionary.
        """
        number = Schema.extract({**basic_data, **integer_data})
        assert isinstance(number, Type)
        assert isinstance(number, Numeric)
        assert is_dataclass(number)
        assert number.type == "integer"

        assert number.minimum is None
        assert number.maximum is None
        assert number.exclusive_minimum is None
        assert number.exclusive_maximum is None
        assert number.multiple_of is None

    def test_extract_number(self, basic_data, number_data):
        """
        Test that the Numeric schema can be extracted from a dictionary.
        """
        number = Schema.extract({**basic_data, **number_data})
        assert isinstance(number, Type)
        assert isinstance(number, Numeric)
        assert is_dataclass(number)
        assert number.type == "number"

        assert number.minimum is None
        assert number.maximum is None
        assert number.exclusive_minimum is None
        assert number.exclusive_maximum is None
        assert number.multiple_of is None


class TestNull:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Null.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
        }
        assert issubclass(Null.KeyWords, KeyWords)

    def test_extract(self, basic_data, null_data):
        """
        Test that the Null schema can be extracted from a dictionary.
        """
        null = Schema.extract({**basic_data, **null_data})
        assert isinstance(null, Type)
        assert isinstance(null, Null)
        assert is_dataclass(null)
        assert null.type == "null"


class TestObject:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Object.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "PROPERTIES": "properties",
            "PATTERN_PROPERTIES": "patternProperties",
            "ADDITIONAL_PROPERTIES": "additionalProperties",
            "MAX_PROPERTIES": "maxProperties",
            "MIN_PROPERTIES": "minProperties",
            "REQUIRED": "required",
            "DEPENDENCIES": "dependencies",
        }
        assert issubclass(Object.KeyWords, KeyWords)

    def test_extract(self, basic_data, object_data):
        """
        Test that the Object schema can be extracted from a dictionary.
        """
        obj = Schema.extract({**basic_data, **object_data})
        assert isinstance(obj, Type)
        assert isinstance(obj, Object)
        assert is_dataclass(obj)
        assert obj.type == "object"

        assert obj.properties is not None
        assert isinstance(obj.properties, dict)
        assert len(obj.properties) == 2

        for key, value in obj.properties.items():
            assert isinstance(value, Type)

            if key == "property1":
                assert isinstance(value, String)
                assert value.type == "string"
            elif key == "property2":
                assert isinstance(value, Numeric)
                assert value.type == "number"
            else:
                raise AssertionError(f"Unexpected property key: {key}")

        assert obj.pattern_properties is None
        assert obj.required == ["property1"]
        assert obj.additional_properties is None
        assert obj.max_properties is None
        assert obj.min_properties is None
        assert obj.dependencies is None

    def test_pattern_extract(self, basic_data, pattern_object_data):
        """
        Test that the Object schema can be extracted from a dictionary with pattern properties.
        """
        type_ = Type.extract({**basic_data, **pattern_object_data})
        assert isinstance(type_, Type)
        assert isinstance(type_, Object)
        assert is_dataclass(type_)
        assert type_.type == "object"

        assert type_.pattern_properties is not None
        assert isinstance(type_.pattern_properties, dict)
        assert len(type_.pattern_properties) == 2

        for key, value in type_.pattern_properties.items():
            assert isinstance(value, Type)

            if key == "^pattern_.*":
                assert isinstance(value, String)
                assert value.type == "string"
            elif key == "^pattern_property2$":
                assert isinstance(value, Numeric)
                assert value.type == "number"
            else:
                raise AssertionError(f"Unexpected pattern property key: {key}")

        assert type_.properties is None
        assert type_.required is None
        assert type_.additional_properties is False
        assert type_.max_properties is None
        assert type_.min_properties is None
        assert type_.dependencies is None


class TestString:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert String.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "TYPE": "type",
            "DEFINITIONS": "definitions",
            "ENUM": "enum",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
            "PATTERN": "pattern",
            "MIN_LENGTH": "minLength",
            "MAX_LENGTH": "maxLength",
        }
        assert issubclass(String.KeyWords, KeyWords)

    def test_extract(self, basic_data, string_data, manager):
        """
        Test that the String schema can be extracted from a dictionary.
        """
        type_ = Schema.extract({**basic_data, **string_data})
        assert isinstance(type_, Type)
        assert isinstance(type_, String)
        assert is_dataclass(type_)
        assert type_.type == "string"

        assert type_.min_length is None
        assert type_.max_length is None
        assert type_.pattern is None
