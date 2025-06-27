from __future__ import annotations

import json
from collections.abc import Mapping
from enum import StrEnum
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

import yaml
from semantic_version import Version

from rad import resources

from ._errors import NoSchemaDefinitionsError, NoSchemaIdError, SchemaIdExistsError
from ._schema import Schema


class ManifestType(StrEnum):
    LATEST = "latest"
    STATIC = "static"


class Manager(Mapping[str, Schema]):
    """
    A manager for schemas that allows for easy access and manipulation of schemas.
    It implements the Mapping interface to provide dictionary-like access to schemas.
    """

    def __init__(
        self,
        schemas: dict[str, Schema] | None = None,
        files_: Traversable | None = None,
        uri_prefix: str | None = None,
    ) -> None:
        self._schemas = schemas or {}
        self._files = files_ or files(resources)
        self._uri_prefix = uri_prefix or "asdf://stsci.edu/datamodels/roman/"

        self._datamodels_manifest_file = self._get_manifest_file(ManifestType.LATEST)
        self._static_manifest_file = self._get_manifest_file(ManifestType.STATIC)
        self._tag_to_uri = self._create_tag_to_uri()

    def _get_manifest_file(self, manifest_type: ManifestType) -> Path | None:
        glob_pattern = "datamodels-*.yaml" if manifest_type == ManifestType.LATEST else "static-*.yaml"

        manifest = None
        for file in (self._files / "manifests").glob(glob_pattern):
            v = Version("1.0.0" if (vn := file.stem.split("-")[-1]) == "1.0" else vn)
            if manifest is None:
                manifest = (file, v)

            if v > manifest[1]:
                manifest = (file, v)

        return manifest[0]

    def _create_tag_to_uri(self) -> dict[str, str]:
        def create_map(file: Path) -> dict[str, str]:
            with file.open("r") as f:
                manifest = yaml.safe_load(f)["tags"]

            tag_to_uri = {}
            for entry in manifest:
                tag_to_uri[entry["tag_uri"]] = entry["schema_uri"]

            return tag_to_uri

        return {**create_map(self._datamodels_manifest_file), **create_map(self._static_manifest_file)}

    @classmethod
    def from_rad(cls) -> Manager:
        """
        Create a Manager instance from the rad resource manager.
        This method is used to initialize the manager with schemas defined in the rad package.
        """
        new = cls()
        for schema_uri in new._tag_to_uri.values():
            new._add_from_uri(schema_uri)

        new._fill_ssc()

        return new

    def _fill_ssc(self) -> None:
        for file in (self._files / "schemas" / "SSC").glob("**/*.yaml"):
            with file.open("r") as f:
                schema = Schema.extract(yaml.safe_load(f))
                if schema.id is None:
                    raise NoSchemaIdError()
                self.register(schema)

    def _add_from_uri(self, uri: str) -> Schema:
        with (self._files / f"{uri.split(self._uri_prefix)[-1]}.yaml").open("r") as f:
            self.register(Schema.extract(yaml.safe_load(f)))

    def _get_subschema(self, uri: str, definition: str) -> Schema:
        schema = self[uri]
        if schema.definitions is None:
            raise NoSchemaDefinitionsError(uri)

        return schema.definitions[definition]

    def __getitem__(self, key: str) -> Schema:
        if "#/definitions/" in key:
            return self._get_subschema(*key.split("#/definitions/"))

        if key not in self._schemas:
            if key in self._tag_to_uri:
                key = self._tag_to_uri[key]
            else:
                self._add_from_uri(key)

        return self._schemas[key]

    def __iter__(self):
        return iter(self._schemas)

    def __len__(self) -> int:
        return len(self._schemas)

    def register(self, schema: Schema) -> None:
        """
        Register a new schema in the manager.
        If a schema with the same name already exists, it will be replaced.
        """

        if schema.id is None:
            raise NoSchemaIdError()

        if schema.id in self._schemas:
            raise SchemaIdExistsError(schema.id)

        self._schemas[schema.id] = schema

    def archive_data(self, uri: str) -> dict[str, Any] | None:
        """
        Archive the data of a schema identified by its URI.
        This method is used to save the schema data in a structured format.
        """

        return self[uri].archive_data(uri.split("/")[-1].split("-")[0], self)

    def create_archive(self, save_path: Path | None = None) -> dict[str, Any]:
        """
        Create an archive of all schemas in the manager.
        This method returns a dictionary containing the archived data of all schemas.
        """

        resolved = []
        for address in list(self.keys()):
            schema = self[address]
            if hasattr(schema, "archive_meta") and schema.archive_meta is not None:
                print(f"    Resolving {address} with archive_meta")
                resolved.append(self.archive_data(address))

        with save_path.open("w") as f:
            json.dump(resolved, f, indent=2)
