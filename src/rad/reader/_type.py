from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Self

from ._errors import ResolutionError, UnhandledKeyError, UnreadableDataError
from ._reader import ValueKeys, rad
from ._schema import Schema

if TYPE_CHECKING:
    from ._manager import Manager

__all__ = ("Type",)


class Type(Schema):
    """
    Type schema for the reader.
        See: https://json-schema.org/draft-04/draft-zyp-json-schema-04#rfc.section.3.5
    """

    type: str | None = rad()

    class TypeKeys(ValueKeys):
        ARRAY = "array"
        BOOLEAN = "boolean"
        INTEGER = "integer"
        NUMBER = "number"
        NULL = "null"
        OBJECT = "object"
        STRING = "string"

        @classmethod
        def reader(cls, data: dict[str, Any]) -> type[Type]:
            """
            Get the reader class for a given type value.

            Parameters
            ----------
            data
                The data dictionary to determine the schema class.

            Returns
            -------
                The schema class corresponding to the value.
            """
            match data.get("type"):
                case cls.ARRAY:
                    return Array
                case cls.BOOLEAN:
                    return Boolean
                case cls.INTEGER | cls.NUMBER:
                    return Numeric
                case cls.NULL:
                    return Null
                case cls.OBJECT:
                    return Object
                case cls.STRING:
                    return String

            raise UnhandledKeyError(f"Unhandled type value: {data.get('type')}.")

    @classmethod
    def extract(cls, data: dict[str, Any]) -> Self:
        """
        Extract a schema instance from a dictionary.

        Parameters
        ----------
        data:
            The data dictionary to read the schema from

        Returns
        -------
            An instance of the schema class.
        """
        if cls is Type:
            if "type" not in data:
                raise UnreadableDataError("Missing 'type' key in data.")

            return cls.TypeKeys.reader(data).extract(data)
        return super().extract(data)


class Array(Type):
    """
    Array schema for the reader.
        See: https://json-schema.org/draft-04/draft-zyp-json-schema-04#rfc.section.3.5.1
    """

    items: list[Schema] | Schema | None = rad()
    # These are not useful for the parser's application, but are part of the
    #   JSON-schema draft-04 specification, so are included for completeness.
    additional_items: bool | None = rad()
    min_items: int | None = rad()
    max_items: int | None = rad()
    unique_items: bool | None = rad()

    def __post_init__(self) -> None:
        """
        Post-initialization to finish processing the items
        """
        super().__post_init__()
        self.type = self.TypeKeys.ARRAY.value

        if isinstance(self.items, Sequence):
            self.items = [Schema.extract(self.simplify(item)) for item in self.items]
        elif isinstance(self.items, Mapping):
            self.items = [Schema.extract(self.simplify(self.items))]
        elif self.items is not None:
            raise UnreadableDataError(f"Expected 'items' to be a list, dict, or Schema instance, got {type(self.items)}.")

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        if self.items is None:
            return data

        items = []
        for index, item in enumerate(self.items):
            entry = item.archive_data(name if len(self.items) == 1 else f"{name}_{index}", manager)
            if entry is not None:
                items.append(entry)

        if not items:
            return data

        data = data or self._archive_data_header(name)
        data["items"] = items

        return data


class Boolean(Type):
    """Boolean schema for the region"""

    def __post_init__(self):
        """
        Post-initialization to ensure properties are processed correctly.
        """
        super().__post_init__()
        self.type = self.TypeKeys.BOOLEAN.value


class Numeric(Type):
    """
    Numeric schema for the reader.
        See: https://json-schema.org/draft-04/draft-fge-json-schema-validation-00#rfc.section.5.1
    """

    # These are not useful for the parser's application, but are part of the
    #   JSON-schema draft-04 specification, so are included for completeness.
    minimum: float | None = rad()
    maximum: float | None = rad()
    exclusive_minimum: bool | None = rad()
    exclusive_maximum: bool | None = rad()
    multiple_of: float | None = rad()

    def __post_init__(self):
        """
        Post-initialization to ensure properties are processed correctly.
        """
        super().__post_init__()
        if self.type is None:
            self.type = self.TypeKeys.NUMBER.value


class Null(Type):
    """
    Null schema for the reader.
        Note: In JSON Schema Draft-04, null types do not have specific keys.
    """

    def __post_init__(self):
        """
        Post-initialization to ensure properties are processed correctly.
        """
        super().__post_init__()
        self.type = self.TypeKeys.NULL.value


class Object(Type):
    """
    Object schema for the reader.
        See: https://json-schema.org/draft-04/draft-fge-json-schema-validation-00#rfc.section.5.4
    """

    properties: dict[str, Schema] | None = rad()
    pattern_properties: dict[str, Schema] | None = rad()
    required: list[str] | None = rad()
    additional_properties: bool | None = rad()
    # These are not useful for the parser's application, but are part of the
    #   JSON-schema draft-04 specification, so are included for completeness.
    max_properties: int | None = rad()
    min_properties: int | None = rad()
    dependencies: dict[str, Any] | None = rad()

    def __post_init__(self):
        """
        Post-initialization to ensure properties are processed correctly.
        """
        super().__post_init__()
        self.type = self.TypeKeys.OBJECT.value

        if self.properties is not None:
            self.properties = {key: Schema.extract(self.simplify(value)) for key, value in self.properties.items()}

        if self.pattern_properties is not None:
            self.pattern_properties = {
                key: Schema.extract(self.simplify(value)) for key, value in self.pattern_properties.items()
            }

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        if self.pattern_properties is not None:
            for key, schema in self.pattern_properties.items():
                if schema.archive_data(key, manager) is not None:
                    raise ResolutionError("Cannot archive data contained within pattern properties")

        if self.properties is None:
            return data

        properties = []
        for key, schema in self.properties.items():
            entry = schema.archive_data(key, manager)
            if entry is not None:
                properties.append(entry)

        if not properties:
            return data

        data = data or self._archive_data_header(name)
        data["properties"] = properties

        return data


class String(Type):
    """
    String schema for the reader.
        See: https://json-schema.org/draft-04/draft-fge-json-schema-validation-00#rfc.section.5.2
    """

    pattern: str | None = rad()
    min_length: int | None = rad()
    max_length: int | None = rad()

    def __post_init__(self):
        """
        Post-initialization to ensure properties are processed correctly.
        """
        super().__post_init__()
        self.type = self.TypeKeys.STRING.value
