from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from dataclasses import Field, dataclass, field, fields
from enum import EnumMeta, StrEnum, unique
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from ._manager import Manager

__all__ = ("Reader", "ValueKeys", "rad")


def rad(schema_key: str | None = None, **kwargs) -> Field:
    """Create a dataclass field with schema metadata.

    Parameters
    ----------
    schema_key, optional
        The key to use for the schema metadata, by default None

    Returns
    -------
        A dataclass field with the specified metadata.
    """
    metadata = kwargs.pop("metadata", {})
    metadata["schema_key"] = schema_key
    return field(metadata=metadata, **kwargs)


@unique
class KeyWords(StrEnum):
    """Enumeration of the keywords used in the schema component"""

    @property
    def reader_name(self) -> str:
        """Get the reader name for the keyword."""
        return self.name.lower()

    @staticmethod
    def snake_to_camel(snake_case_string: str) -> str:
        """
        Converts a snake_case string to camelCase.

        Args:
            snake_case_string (str): The string in snake_case format.

        Returns:
            str: The converted string in camelCase format.
        """
        words = snake_case_string.split("_")
        # Capitalize the first letter of each word except the first one
        camel_case_words = [words[0]] + [word.capitalize() for word in words[1:]]
        return "".join(camel_case_words)

    @classmethod
    def extract(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract the keywords from the data dictionary.

        Parameters
        ----------
        data:
            The data dictionary to extract the keywords from

        Returns
        -------
            A dictionary with the keywords as keys and their values.
        """
        return {key.reader_name: data.get(key) for key in cls}

    @classmethod
    def new(cls, schema: Reader) -> type[KeyWords]:
        """
        Create a new enumeration for the schema's keywords.

        Parameters
        ----------
        schema:
            The schema to create the keywords for

        Returns
        -------
            A new enumeration class with the schema's keywords.
        """
        key_words: list[tuple[str, str]] = []
        for field_ in fields(schema):
            if "schema_key" in field_.metadata:
                name = field_.name.upper()
                schema_key = field_.metadata["schema_key"]

                if schema_key is None:
                    schema_key = cls.snake_to_camel(field_.name)

                key_words.append((name, schema_key))

        return unique(cls("KeyWords", key_words))


@dataclass
class Reader(ABC):
    """
    Base class for schema metadata reading
    """

    @property
    @abstractmethod
    def KeyWords(self) -> type[KeyWords]:
        """
        Get the enumeration for the schema's syntax keywords

        Note
        ----
        This is only an abstract property so that subclasses are forced to implement it,
        it is intended to a subclass of `KeyWords` that defined within the parser object.
        """

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls = dataclass(cls)
        cls.KeyWords = KeyWords.new(cls)

    @property
    def data(self) -> dict[str, Any]:
        """
        Get the data representation of the schema.

        Returns
        -------
            A dictionary representation of the schema.
        """
        data = {}
        for keyword in self.KeyWords:
            value = getattr(self, keyword.reader_name, None)
            if value is not None:
                data[keyword.value] = value
        return data

    @staticmethod
    def simplify(data: dict[str, Any] | Reader) -> dict[str, Any]:
        """
        Simplify the data dictionary by removing None values.

        Parameters
        ----------
        data:
            The data dictionary to simplify

        Returns
        -------
            A simplified dictionary with None values removed.
        """
        if isinstance(data, Reader):
            data = data.data
        return data

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
        return cls(**cls.KeyWords.extract(data))

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        return None


class _AbstractStrEnumMeta(ABCMeta, EnumMeta): ...


class ValueKeys(ABC, StrEnum, metaclass=_AbstractStrEnumMeta):
    """Abstract base class for value keys in schemas."""

    @classmethod
    @abstractmethod
    def reader(cls, data: dict[str, Any]) -> type[Reader]:
        """
        Select the schema class based on the value.

        Parameters
        ----------
        data
            The data dictionary to determine the schema class.

        Returns
        -------
            The schema class corresponding to the value.
        """
