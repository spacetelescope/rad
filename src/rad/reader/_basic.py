from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._reader import Reader, rad

if TYPE_CHECKING:
    from ._manager import Manager

__all__ = ("Basic",)


class Root(Reader):
    """
    Root schema for the reader.
        See: https://json-schema.org/draft-04/draft-zyp-json-schema-04
    """

    id: str | None = rad()
    schema: str | None = rad("$schema")


class Metadata(Reader):
    """
    Metadata schema for the reader.
        See: https://json-schema.org/draft-04/draft-fge-json-schema-validation-00#rfc.section.6
    """

    title: str | None = rad()
    description: str | None = rad()
    default: str | None = rad()


class ArchiveCatalog(Reader):
    """
    Read archive information for MAST
    """

    datatype: str | None = rad()
    destination: list[str] | None = rad()

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any]:
        return {
            "datatype": self.datatype,
            "destination": self.destination,
        }


class Rad(Reader):
    """
    Custom information for RAD
    """

    archive_catalog: ArchiveCatalog | None = rad("archive_catalog")
    unit: str | None = rad()
    datamodel_name: str | None = rad("datamodel_name")
    archive_meta: str | None = rad("archive_meta")

    def __post_init__(self) -> None:
        """
        Post-initialization method to set the archive metadata.
        """
        if self.archive_catalog is not None:
            self.archive_catalog = ArchiveCatalog.extract(self.simplify(self.archive_catalog))

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = {"archive_meta": self.archive_meta} if self.archive_meta else None

        if self.archive_catalog is not None:
            data = data or {}
            data.update(self.archive_catalog.archive_data(name, manager))

        return data


class Basic(Root, Metadata, Rad):
    """Basic schema for the reader."""

    def _archive_data_header(self, name: str) -> dict[str, Any]:
        header = {"name": name}

        if self.title:
            header["title"] = self.title

        if self.description:
            header["description"] = self.description

        return header

    def archive_data(self, name: str, manager: Manager) -> dict[str, Any] | None:
        data = super().archive_data(name, manager)

        if data is None:
            return None

        header = self._archive_data_header(name)
        header.update(data)

        return header
