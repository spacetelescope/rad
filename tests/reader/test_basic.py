from dataclasses import is_dataclass

from rad.reader._basic import ArchiveCatalog, Basic, Metadata, Rad, Root
from rad.reader._reader import KeyWords


class TestRoot:
    def test_keywords(self):
        """
        Test that the Root schema has the correct keywords.
        """
        assert Root.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
        }
        assert issubclass(Root.KeyWords, KeyWords)

    def test_extract(self, root_data):
        """
        Test that the Root schema can be extracted from a dictionary.
        """
        root = Root.extract(root_data)
        assert isinstance(root, Root)
        assert is_dataclass(root)
        assert root.id == "test_id"
        assert root.schema == "http://example.com/schema"


class TestMetadata:
    def test_keywords(self):
        """
        Test that the Metadata schema has the correct keywords.
        """
        assert Metadata.KeyWords.__members__ == {
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
        }
        assert issubclass(Metadata.KeyWords, KeyWords)

    def test_extract(self, metadata_data):
        """
        Test that the Metadata schema can be extracted from a dictionary.
        """
        metadata = Metadata.extract(metadata_data)

        assert isinstance(metadata, Metadata)
        assert is_dataclass(metadata)
        assert metadata.title == "Test Title"
        assert metadata.description == "Test Description"
        assert metadata.default == "Test Default"


class TestArchiveCatalog:
    def test_keywords(self):
        """
        Test that the ArchiveCatalog schema has the correct keywords.
        """
        assert ArchiveCatalog.KeyWords.__members__ == {
            "DATATYPE": "datatype",
            "DESTINATION": "destination",
        }
        assert issubclass(ArchiveCatalog.KeyWords, KeyWords)

    def test_extract(self, archive_catalog_data):
        """
        Test that the ArchiveCatalog schema can be extracted from a dictionary.
        """
        archive_catalog = ArchiveCatalog.extract(archive_catalog_data)
        assert isinstance(archive_catalog, ArchiveCatalog)
        assert is_dataclass(archive_catalog)
        assert archive_catalog.datatype == "Test DataType"
        assert archive_catalog.destination == ["destination1", "destination2"]

    def test_archive_data(self, manager, archive_catalog_data):
        """
        Test that the archive_data method returns the correct data.
        """
        archive_catalog = ArchiveCatalog.extract(archive_catalog_data)
        data = archive_catalog.archive_data("test_name", manager)
        assert data == {
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }


class TestRad:
    def test_keywords(self):
        """
        Test that the Rad schema has the correct keywords.
        """
        assert Rad.KeyWords.__members__ == {
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
        }
        assert issubclass(Rad.KeyWords, KeyWords)

    def test_extract(self, rad_data, archive_catalog_data):
        """
        Test that the Rad schema can be extracted from a dictionary.
        """
        rad = Rad.extract({**rad_data, "archive_catalog": archive_catalog_data})
        assert isinstance(rad, Rad)
        assert is_dataclass(rad)

        assert rad.datamodel_name == "Test DataModel Name"
        assert rad.archive_meta == "Test Archive Meta"
        assert rad.unit == "Test Unit"

        assert isinstance(rad.archive_catalog, ArchiveCatalog)
        assert rad.archive_catalog.datatype == "Test DataType"
        assert rad.archive_catalog.destination == ["destination1", "destination2"]

    def test_archive_data_full(self, manager, rad_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        rad = Rad.extract({**rad_data, "archive_catalog": archive_catalog_data})
        assert rad.archive_data("test_name", manager) == {
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }

    def test_archive_data_no_catalog(self, manager, rad_data):
        """
        Test that the archive_data method works when no archive_catalog
        """

        rad = Rad.extract(rad_data)
        assert rad.archive_data("test_name", manager) == {"archive_meta": "Test Archive Meta"}

    def test_archive_data_no_meta(self, manager, rad_data, archive_catalog_data):
        """
        Test that the archive_data method works when no archive_meta
        """
        data = dict(rad_data)
        del data["archive_meta"]

        rad = Rad.extract({**data, "archive_catalog": archive_catalog_data})
        assert rad.archive_data("test_name", manager) == {
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }

    def test_archive_data_no_archive_info(self, manager, rad_data):
        """
        Test that the archive_data method works when no archive information is present
        """
        data = dict(rad_data)
        del data["archive_meta"]

        rad = Rad.extract(data)
        assert rad.archive_data("test_name", manager) is None


class TestBasic:
    def test_keywords(self):
        """
        Test that the Basic schema has the correct keywords.
        """
        assert Basic.KeyWords.__members__ == {
            "ID": "id",
            "SCHEMA": "$schema",
            "TITLE": "title",
            "DESCRIPTION": "description",
            "DEFAULT": "default",
            "ARCHIVE_CATALOG": "archive_catalog",
            "UNIT": "unit",
            "DATAMODEL_NAME": "datamodel_name",
            "ARCHIVE_META": "archive_meta",
        }
        assert issubclass(Basic.KeyWords, KeyWords)

    def test_extract(self, basic_data, archive_catalog_data):
        """
        Test that the Basic schema can be extracted from a dictionary.
        """
        basic = Basic.extract({**basic_data, "archive_catalog": archive_catalog_data})
        assert isinstance(basic, Basic)
        assert isinstance(basic, Root)
        assert isinstance(basic, Metadata)
        assert isinstance(basic, Rad)
        assert is_dataclass(basic)
        assert basic.id == "test_id"
        assert basic.schema == "http://example.com/schema"
        assert basic.title == "Test Title"
        assert basic.description == "Test Description"
        assert basic.default == "Test Default"

        assert basic.unit == "Test Unit"
        assert basic.datamodel_name == "Test DataModel Name"
        assert basic.archive_meta == "Test Archive Meta"

        assert isinstance(basic.archive_catalog, ArchiveCatalog)
        assert basic.archive_catalog.datatype == "Test DataType"
        assert basic.archive_catalog.destination == ["destination1", "destination2"]

    def test_archive_data_full(self, manager, basic_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        basic = Basic.extract({**basic_data, "archive_catalog": archive_catalog_data})
        assert basic.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "description": "Test Description",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }

    def test_archive_data_missing_title_and_description(self, manager, basic_data, archive_catalog_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        data = dict(basic_data)
        del data["title"]

        basic = Basic.extract({**data, "archive_catalog": archive_catalog_data})
        assert basic.archive_data("test_name", manager) == {
            "name": "test_name",
            "description": "Test Description",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }

        data = dict(basic_data)
        del data["description"]

        basic = Basic.extract({**data, "archive_catalog": archive_catalog_data})
        assert basic.archive_data("test_name", manager) == {
            "name": "test_name",
            "title": "Test Title",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }
        del data["title"]

        basic = Basic.extract({**data, "archive_catalog": archive_catalog_data})
        assert basic.archive_data("test_name", manager) == {
            "name": "test_name",
            "archive_meta": "Test Archive Meta",
            "datatype": "Test DataType",
            "destination": ["destination1", "destination2"],
        }

    def test_archive_data_missing_archive_info(self, manager, basic_data):
        """
        Test that the archive_data method works correctly on the full set of data
        """

        data = dict(basic_data)
        del data["archive_meta"]

        basic = Basic.extract(data)
        assert basic.archive_data("test_name", manager) is None
