from dataclasses import dataclass, fields, is_dataclass

import pytest

from rad.reader._reader import KeyWords, Reader, rad


class TestKeyWords:
    class ExampleKeyWords(KeyWords):
        """
        Test class for KeyWords enumeration.
        """

        KEY_ONE: str = "keyOne"
        KEY_TWO: str = "keyTwo"

    @dataclass
    class ExampleSchema:
        bar: str = rad()
        baz_box: str = rad()
        baz: str = rad("$baz")

    def test_reader_name(self):
        """
        Test that a reader name is generated for each keyword.
        """
        assert self.ExampleKeyWords.KEY_ONE.reader_name == "key_one" == self.ExampleKeyWords.KEY_ONE.name.lower()
        assert self.ExampleKeyWords.KEY_TWO.reader_name == "key_two" == self.ExampleKeyWords.KEY_TWO.name.lower()

    @pytest.mark.parametrize(
        "data",
        [
            {"keyOne": "value1", "keyTwo": "value2", "otherKey": "value3"},
            {"keyOne": "value1", "otherKey": "value3"},
            {"keyTwo": "value2", "otherKey": "value3"},
            {"otherKey": "value3"},
            {"key_one": "value1", "key_two": "value2", "other_key": "value3"},
        ],
    )
    def test_extract(self, data):
        assert self.ExampleKeyWords.extract(data) == {
            self.ExampleKeyWords.KEY_ONE.reader_name: data.get("keyOne"),
            self.ExampleKeyWords.KEY_TWO.reader_name: data.get("keyTwo"),
        }

    def test_new(self):
        """
        Test that a new KeyWords enumeration can be created from a schema.
        """
        NewKeyWords = KeyWords.new(self.ExampleSchema)
        assert NewKeyWords.__members__ == {
            "BAR": "bar",
            "BAZ_BOX": "bazBox",
            "BAZ": "$baz",
        }
        assert issubclass(NewKeyWords, KeyWords)


class TestReader:
    class ExampleReader(Reader):
        bar: str = rad()
        baz_box: str = rad()
        baz: str = rad("$baz")

    def test_reader(self):
        """
        Test that the schema is correctly defined and fields are set up.
        """
        assert set(field.name for field in fields(self.ExampleReader)) == {"bar", "baz_box", "baz"}
        assert self.ExampleReader.KeyWords.__members__ == {
            "BAR": "bar",
            "BAZ_BOX": "bazBox",
            "BAZ": "$baz",
        }
        assert issubclass(self.ExampleReader.KeyWords, KeyWords)
        assert is_dataclass(self.ExampleReader)

    @pytest.mark.parametrize(
        "data",
        [
            {"bar": "value1", "bazBox": "value2", "$baz": "value3"},
            {"bar": "value1", "bazBox": "value2"},
            {"bar": "value1"},
            {"bar": "value1", "bazBox": "value2", "$baz": "value3", "test": "other"},
        ],
    )
    def test_extract(self, data):
        """
        Test that we can extract data
        """

        extract = self.ExampleReader.extract(data)
        for field in fields(self.ExampleReader):
            if "schema_key" in field.metadata:
                key = field.metadata["schema_key"]
                if key is None:
                    key = KeyWords.snake_to_camel(field.name)
                assert getattr(extract, field.name) == data.get(key, None), f"Failed for {field.name} with key {key}"

    def test_archive_data(self, manager):
        """
        Test that the archive_data method returns None by default.
        """
        reader = self.ExampleReader.extract({"bar": "value1", "bazBox": "value2", "$baz": "value3"})
        assert reader.archive_data("test_name", manager) is None
