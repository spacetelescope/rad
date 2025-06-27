from __future__ import annotations

from abc import abstractmethod
from re import match
from typing import TYPE_CHECKING, Any

from ._reader import rad
from ._schema import Schema

if TYPE_CHECKING:
    from ._manager import Manager


class Link(Schema):
    """
    Type for links in the reader.
    """

    EXTERNAL_LINKS = frozenset(
        (
            r"tag:stsci.edu:asdf/time/time-1.*",
            r"tag:stsci.edu:asdf/core/ndarray-1.*",
            r"tag:stsci.edu:asdf/unit/quantity-1.*",
            r"tag:stsci.edu:asdf/unit/unit-1.*",
            r"tag:astropy.org:astropy/units/unit-1.*",
            r"tag:astropy.org:astropy/table/table-1.*",
            r"tag:stsci.edu:gwcs/wcs-*",
            r"http://stsci.edu/schemas/asdf/time/time-1.*",
        )
    )

    @property
    def is_external(self) -> bool:
        """
        Check if the link is external.

        Returns
        -------
            True if the link is external, False otherwise.
        """
        for pattern in self.EXTERNAL_LINKS:
            if match(pattern, self.link):
                return True

        return False

    @property
    @abstractmethod
    def link(self) -> str:
        """
        The link address for the schema.

        Returns
        -------
            The link address.
        """

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        if self.is_external:
            return super().archive_data(name, manager)

        return manager[self.link].archive_data(name, manager)


class Ref(Link):
    """
    Type $ref schema for the reader.
    """

    ref: str = rad("$ref")

    @property
    def link(self) -> str:
        """
        The link address for the schema.

        Returns
        -------
            The link address.
        """
        if match(r".*#/definitions$", self.ref):
            return self.ref.split("#/definitions")[0]

        return self.ref


class Tag(Link):
    """
    Type tag schema for the reader.
    """

    tag: str = rad()

    @property
    def link(self) -> str:
        """
        The link address for the schema.

        Returns
        -------
            The link address.
        """
        return self.tag
