from dataclasses import is_dataclass

import pytest

from rad.reader._link import Link, Ref, Tag
from rad.reader._manager import Manager
from rad.reader._reader import KeyWords
from rad.reader._schema import AllOf, Schema
from rad.reader._type import Object


class TestRef:
    def test_keywords(self):
        """
        Test that the Ref schema has the correct keywords.
        """

        assert Ref.KeyWords.__members__ == {
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
            "REF": "$ref",
        }
        assert issubclass(Ref.KeyWords, KeyWords)

    def test_extract(self, basic_data, top_ref_data):
        """Test that a Ref schema can be extracted correctly from a schema."""

        schema_ = Schema.extract({**basic_data, **top_ref_data})

        assert isinstance(schema_, Schema)
        assert isinstance(schema_, AllOf)

        assert isinstance(schema_.all_of, list)
        assert schema_.all_of
        assert len(schema_.all_of) == 1

        ref = schema_.all_of[0]
        assert isinstance(ref, Schema)
        assert isinstance(ref, Link)
        assert isinstance(ref, Ref)
        assert is_dataclass(ref)

        assert ref.ref == "http://example.com/ref_schema"

    def test_archive_data_interal(self):
        """Test link out to an internal schema"""

        data = {"$ref": "asdf://stsci.edu/datamodels/roman/schemas/basic-1.0.0"}
        schema = Schema.extract(data)
        assert schema.archive_data("test", Manager.from_rad()) == {
            "name": "test",
            "title": "Basic Information",
            "properties": [
                {
                    "name": "calibration_software_name",
                    "title": "Calibration Software Name",
                    "datatype": "nvarchar(120)",
                    "destination": [
                        "WFIExposure.calibration_software_name",
                        "GuideWindow.calibration_software_name",
                        "WFICommon.calibration_software_name",
                        "WFIMosaic.calibration_software_name",
                        "SourceCatalog.calibration_software_name",
                        "SegmentationMap.calibration_software_name",
                    ],
                },
                {
                    "name": "calibration_software_version",
                    "title": "Calibration Software Version Number",
                    "datatype": "nvarchar(120)",
                    "destination": [
                        "WFIExposure.calibration_software_version",
                        "GuideWindow.calibration_software_version",
                        "WFICommon.calibration_software_version",
                        "WFIMosaic.calibration_software_version",
                        "SourceCatalog.calibration_software_version",
                        "SegmentationMap.calibration_software_version",
                    ],
                },
                {
                    "name": "product_type",
                    "title": "Product Type Descriptor",
                    "datatype": "nvarchar(120)",
                    "destination": [
                        "WFIExposure.product_type",
                        "GuideWindow.product_type",
                        "WFICommon.product_type",
                        "WFIMosaic.product_type",
                        "SourceCatalog.product_type",
                        "SegmentationMap.product_type",
                    ],
                },
                {
                    "name": "filename",
                    "title": "File Name",
                    "datatype": "nvarchar(120)",
                    "destination": [
                        "WFIExposure.filename",
                        "WFIMosaic.filename",
                        "GuideWindow.filename",
                        "WFICommon.filename",
                        "SourceCatalog.filename",
                        "SegmentationMap.filename",
                    ],
                },
                {
                    "name": "file_date",
                    "title": "File Creation Date",
                    "datatype": "datetime2",
                    "destination": [
                        "WFIExposure.filedate",
                        "GuideWindow.filedate",
                        "WFICommon.filedate",
                        "WFIMosaic.filedate",
                        "SourceCatalog.filedate",
                        "SegmentationMap.filedate",
                    ],
                },
                {
                    "name": "model_type",
                    "title": "Data Model Type",
                    "datatype": "nvarchar(50)",
                    "destination": [
                        "WFIExposure.model_type",
                        "GuideWindow.model_type",
                        "WFICommon.model_type",
                        "WFIMosaic.model_type",
                        "SourceCatalog.model_type",
                        "SegmentationMap.model_type",
                    ],
                },
                {
                    "name": "origin",
                    "title": "Institution / Organization Name",
                    "datatype": "nvarchar(15)",
                    "destination": [
                        "WFIExposure.origin",
                        "GuideWindow.origin",
                        "WFICommon.origin",
                        "WFIMosaic.origin",
                        "SourceCatalog.origin",
                        "SegmentationMap.origin",
                    ],
                },
                {
                    "name": "prd_version",
                    "title": "SOC PRD Version Number",
                    "datatype": "nvarchar(120)",
                    "destination": [
                        "WFIExposure.prd_version",
                        "GuideWindow.prd_version",
                        "WFICommon.prd_version",
                        "WFIMosaic.prd_version",
                        "SourceCatalog.prd_version",
                        "SegmentationMap.prd_version",
                    ],
                },
                {
                    "name": "sdf_software_version",
                    "title": "SDF Version Number",
                    "datatype": "nvarchar(120)",
                    "destination": [
                        "WFIExposure.sdf_software_version",
                        "GuideWindow.sdf_software_version",
                        "WFICommon.sdf_software_version",
                        "WFIMosaic.sdf_software_version",
                        "SourceCatalog.sdf_software_version",
                        "SegmentationMap.sdf_software_version",
                    ],
                },
                {
                    "name": "telescope",
                    "title": "Telescope Name",
                    "datatype": "nvarchar(5)",
                    "destination": [
                        "WFIExposure.telescope",
                        "WFIMosaic.telescope",
                        "GuideWindow.telescope",
                        "WFICommon.telescope",
                        "SourceCatalog.telescope",
                        "SegmentationMap.telescope",
                    ],
                },
            ],
        }


class TestTag:
    def test_keywords(self):
        """
        Test that the Tag schema has the correct keywords.
        """

        assert Tag.KeyWords.__members__ == {
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
            "TAG": "tag",
        }
        assert issubclass(Tag.KeyWords, KeyWords)

    def test_extract(self, basic_data, tag_data):
        """Test that a Tag schema can be extracted correctly from a schema."""

        schema_ = Schema.extract({**basic_data, **tag_data})

        assert isinstance(schema_, Schema)
        assert isinstance(schema_, Object)

        assert isinstance(schema_.properties, dict)
        assert schema_.properties
        assert len(schema_.properties) == 2

        assert "property1" in schema_.properties
        property1 = schema_.properties["property1"]
        assert isinstance(property1, Link)
        assert isinstance(property1, Tag)
        assert is_dataclass(property1)
        assert property1.tag == "asdf://test.com/tags/test_tag1"

        assert "property2" in schema_.properties
        property2 = schema_.properties["property2"]
        assert isinstance(property2, Link)
        assert isinstance(property2, Tag)
        assert is_dataclass(property2)
        assert property2.tag == "asdf://test.com/tags/test_tag2"

    @pytest.mark.parametrize("tag", [tag for tag in Link.EXTERNAL_LINKS if tag.startswith("tag:")])
    def test_archive_data_external(self, manager, tag):
        """
        Test that external tags are resolved correctly
        """
        data = {
            "title": "Test Schema",
            "description": "This is a test schema",
            "tag": tag,
            "archive_catalog": {
                "destination": ["foo", "bar"],
                "datatype": "baz",
            },
        }

        schema = Schema.extract(data)
        assert schema.archive_data("test", manager) == {
            "name": "test",
            "title": "Test Schema",
            "description": "This is a test schema",
            "datatype": "baz",
            "destination": ["foo", "bar"],
        }
