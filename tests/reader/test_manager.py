from re import match

import pytest

from rad.reader._errors import NoSchemaIdError, SchemaIdExistsError
from rad.reader._link import Ref, Tag
from rad.reader._manager import Manager
from rad.reader._reader import rad
from rad.reader._schema import AllOf, Schema
from rad.reader._type import Object


class TestManager:
    class ExampleSchema(Schema):
        """
        Example Schema for testing purposes.
        """

        foo: str = rad()
        bar: str = rad()

    def test_register(self, manager):
        """
        Test Registering a schema in the manager.
        """
        assert len(manager) == 0
        reader = self.ExampleSchema.extract({"id": "test_uri", "foo": "value1", "bar": "value2"})
        manager.register(reader)
        assert len(manager) == 1

        assert "test_uri" in manager
        assert manager["test_uri"] is reader

    def test_register_no_id(self, manager):
        """
        Test that registering a schema without an ID raises an error.
        """
        with pytest.raises(NoSchemaIdError, match=r"Schema must have an 'id' attribute, which is not None."):
            manager.register(self.ExampleSchema.extract({"foo": "value1", "bar": "value2"}))

    def test_register_existing_id(self, manager):
        """
        Test that registering a schema with an existing ID raises an error.
        """
        reader = self.ExampleSchema.extract({"id": "test_uri", "foo": "value1", "bar": "value2"})
        manager.register(reader)
        assert len(manager) == 1

        with pytest.raises(SchemaIdExistsError, match=r"Schema with uri .* already exists."):
            manager.register(self.ExampleSchema.extract({"id": "test_uri", "foo": "value3", "bar": "value4"}))

        assert manager["test_uri"] is reader
        assert reader.foo == "value1"
        assert reader.bar == "value2"

        assert len(manager) == 1

    def test_from_rad(self):
        """
        Test that the manager can load schemas from the rad package.
        """

        manager = Manager.from_rad()
        assert len(manager) == len(manager._tag_to_uri) + len(list((manager._files / "schemas" / "SSC").glob("**/*.yaml")))

        for uri in manager._tag_to_uri.values():
            assert uri in manager
            assert isinstance(manager[uri], Schema)

        wfi_image_regex = r"asdf://stsci.edu/datamodels/roman/schemas/wfi_image-.*$"
        for uri in manager:
            if match(wfi_image_regex, uri):
                wfi_image = manager[uri]
                break
        else:
            raise AssertionError("WFI image schema not found in manager.")

        assert isinstance(wfi_image, Object)
        assert "meta" in wfi_image.properties

        all_of = wfi_image.properties["meta"]
        assert isinstance(all_of, AllOf)

        refs = [ref for ref in all_of.all_of if isinstance(ref, Ref)]
        assert len(refs) == 1
        ref = refs[0]

        common_uri_regex = r"asdf://stsci.edu/datamodels/roman/schemas/common-.*$"
        assert match(common_uri_regex, ref.ref)
        assert ref.ref not in manager._schemas

        common = manager[ref.ref]
        assert ref.ref in manager._schemas
        assert manager[ref.ref] is common

        assert isinstance(common, AllOf)
        common_refs = [r for r in common.all_of if isinstance(r, Ref)]
        assert len(common_refs) == 1
        common_ref = common_refs[0]

        basic_uri_regex = r"asdf://stsci.edu/datamodels/roman/schemas/basic-.*$"
        assert match(basic_uri_regex, common_ref.ref)
        assert common_ref.ref not in manager._schemas

        basic = manager[common_ref.ref]
        assert common_ref.ref in manager._schemas
        assert manager[common_ref.ref] is basic

        assert isinstance(basic, Object)
        assert len(basic.properties) > 0
        for prop in basic.properties.values():
            assert isinstance(prop, Tag)
            assert prop.tag in manager._tag_to_uri
            assert prop.tag not in manager._schemas
            assert manager._tag_to_uri[prop.tag] in manager._schemas
            assert manager[manager._tag_to_uri[prop.tag]] is manager[prop.tag]
