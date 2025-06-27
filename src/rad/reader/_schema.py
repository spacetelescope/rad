from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from ._basic import Basic
from ._errors import ResolutionError, UnhandledKeyError, UnreadableDataError
from ._reader import ValueKeys, rad

if TYPE_CHECKING:
    from ._manager import Manager


class Schema(Basic):
    """
    Main reader object
    """

    definitions: dict[str, Schema] | None = rad()
    enum: list[str] | None = rad()

    class Selectors(ValueKeys):
        """
        Enumeration for schema selectors.
        """

        ALL_OF = "allOf"
        ANY_OF = "anyOf"
        NOT = "not"
        ONE_OF = "oneOf"
        TYPE = "type"
        REF = "$ref"
        TAG = "tag"

        @classmethod
        def reader(cls, object_type: type[object], data: dict[str, any]) -> type[Schema] | None:
            """
            Get the reader class for a given selector value.

            Parameters
            ----------
            object_type
                The type of the object to read.

            data
                The data dictionary to determine the schema class.

            Returns
            -------
                The schema class corresponding to the value.
            """
            from ._link import Ref, Tag
            from ._type import Type

            if sum(True for key in cls if data.get(key) is not None) > 1:
                raise UnhandledKeyError(
                    f"Multiple schema selectors found in data: {', '.join(key for key in cls if data.get(key) is not None)}."
                )

            if cls.TYPE in data and not issubclass(object_type, Type):
                return Type

            if cls.ALL_OF in data and not issubclass(object_type, AllOf):
                return AllOf

            if cls.ANY_OF in data and not issubclass(object_type, AnyOf):
                return AnyOf

            if cls.NOT in data and not issubclass(object_type, Not):
                return Not

            if cls.ONE_OF in data and not issubclass(object_type, OneOf):
                return OneOf

            if cls.REF in data and not issubclass(object_type, Ref):
                return Ref

            if cls.TAG in data and not issubclass(object_type, Tag):
                return Tag

            return None

    @classmethod
    def extract(cls, data: dict[str, Any] | None) -> Schema:
        """
        Extract a schema instance from a dictionary.

        Parameters
        ----------
        data
            The data dictionary to extract the schema from.

        Returns
        -------
            A Schema instance.
        """
        if (reader := cls.Selectors.reader(cls, data)) is None:
            return super().extract(data)

        return reader.extract(data)

    def __post_init__(self):
        """
        Post-initialization to process definitions
        """
        super().__post_init__()

        if self.definitions is not None:
            if self.Selectors.REF in self.definitions:
                self.definitions = Schema.extract(self.simplify(self.definitions))
            elif isinstance(self.definitions, Mapping):
                self.definitions = {key: Schema.extract(self.simplify(value)) for key, value in self.definitions.items()}
            else:
                raise UnreadableDataError(f"Expected 'definitions' to be a Mapping or a $ref, got {type(self.definitions)}.")


class AllOf(Schema):
    """
    Schema for 'allOf' keyword.
    """

    all_of: list[Schema] = rad()

    def __post_init__(self):
        """Post-initialization to process all_of list."""
        super().__post_init__()

        if self.all_of is not None:
            self.all_of = [Schema.extract(self.simplify(item)) for item in self.all_of]

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        all_of_data = []
        for item in self.all_of:
            item_data = item.archive_data(name, manager)
            if item_data is not None:
                all_of_data.append(item_data)

        if len(all_of_data) == 1:
            data = data or {"name": name}

            if "title" not in data and "title" in all_of_data[0]:
                data["title"] = all_of_data[0]["title"]

            if "description" not in data and "description" in all_of_data[0]:
                data["description"] = all_of_data[0]["description"]

            if "archive_meta" not in data and "archive_meta" in all_of_data[0]:
                data["archive_meta"] = all_of_data[0]["archive_meta"]

            if "datatype" not in data and "datatype" in all_of_data[0]:
                data["datatype"] = all_of_data[0]["datatype"]

            if "destination" not in data and "destination" in all_of_data[0]:
                data["destination"] = all_of_data[0]["destination"]

            for key, value in all_of_data[0].items():
                if key in ("name", "title", "description", "archive_meta", "datatype", "destination"):
                    continue

                if key not in data:
                    data[key] = value
                else:
                    raise ResolutionError(f"Cannot merge {key} with different types in {data}")

            return data

        if not all_of_data:
            return data

        data = data or self._archive_data_header(name)

        if "properties" in all_of_data[0]:
            properties = {}
            for item in all_of_data:
                if "datatype" in item or "destination" in item:
                    raise ResolutionError("Cannot archive 'allOf' with either datatype or destination.")

                new_properties = item["properties"]
                for property_ in new_properties:
                    if property_["name"] in properties:
                        current = properties[property_["name"]]
                        if "title" not in current and "title" in property_:
                            current["title"] = property_["title"]

                        if "description" not in current and "description" in property_:
                            current["description"] = property_["description"]

                        if "archive_meta" not in current and "archive_meta" in property_:
                            current["archive_meta"] = property_["archive_meta"]

                        if current["datatype"] != property_["datatype"]:
                            raise ResolutionError(
                                f"Cannot archive 'allOf' with different datatypes for property '{property_['name']}'."
                            )
                        destination = list(set(current["destination"]).union(set(property_["destination"])))
                        destination.sort()
                        current["destination"] = destination
                    else:
                        properties[property_["name"]] = property_

            data["properties"] = [properties[name] for name in sorted(properties.keys())]
            return data

        if "items" in all_of_data[0]:
            data["items"] = []
            for item in all_of_data:
                if "datatype" in item or "destination" in item:
                    raise ResolutionError("Cannot archive 'allOf' with either datatype or destination.")
                data["items"].extend(item["items"])

            return data

        raise ResolutionError("Cannot archive 'allOf' without properties or items.")


class AnyOf(Schema):
    """
    Schema for 'anyOf' keyword.
    """

    any_of: list[Schema] = rad()

    def __post_init__(self):
        """Post-initialization to process any_of list."""
        super().__post_init__()

        if self.any_of is not None:
            self.any_of = [Schema.extract(self.simplify(item)) for item in self.any_of]

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        any_of_data = []
        for index, item in enumerate(self.any_of):
            item_data = item.archive_data(f"{name}_{index}", manager)
            if item_data is not None:
                any_of_data.append(item_data)

        if not any_of_data:
            return data

        data = data or self._archive_data_header(name)
        data["anyOf"] = any_of_data
        return data


class Not(Schema):
    """
    Schema for 'not' keyword.
    """

    not_: Schema = rad("not")

    def __post_init__(self):
        """Post-initialization to process not_ list."""
        super().__post_init__()

        if self.not_ is not None:
            self.not_ = Schema.extract(self.simplify(self.not_))

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        not_data = self.not_.archive_data(f"{name}_not", manager)

        if not not_data:
            return data

        data = data or self._archive_data_header(name)
        data["not"] = not_data
        return data


class OneOf(Schema):
    """
    Schema for 'oneOf' keyword.
    """

    one_of: list[Schema] = rad()

    def __post_init__(self):
        """Post-initialization to process one_of list."""
        super().__post_init__()

        if self.one_of is not None:
            self.one_of = [Schema.extract(self.simplify(item)) for item in self.one_of]

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        one_of_data = []
        for index, item in enumerate(self.one_of):
            item_data = item.archive_data(f"{name}_{index}", manager)
            if item_data is not None:
                one_of_data.append(item_data)

        if not one_of_data:
            return data

        data = data or self._archive_data_header(name)
        data["oneOf"] = one_of_data
        return data
