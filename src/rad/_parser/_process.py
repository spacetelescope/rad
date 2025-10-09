from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import asdf
import yaml
from semantic_version import Version

from ._archive import archive_entries, archive_schema
from ._ssc import asdf_ssc_config
from ._super_schema import super_schema

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any, TypeDict

    class ArchiveOutput(TypeDict):
        super_schemas: dict[Path, dict[str, Any]]
        archive_schemas: dict[str, dict[str, Any]]
        archive_data: list[str]


def _get_latest_uris() -> Generator[str, None, None]:
    # Find latest datamodels manifest URI
    latest_version = "0.0.0"
    for uri in asdf.get_config().resource_manager:
        if uri.startswith("asdf://stsci.edu/datamodels/roman/manifests/datamodels-"):
            version = uri.rsplit("-", 1)[-1]

            # First manifest has a bad semantic version "1.0", so convert to "1.0.0"
            version = "1.0.0" if version == "1.0" else version

            if Version(version) > Version(latest_version):
                latest_version = version

    datamodels_uri = f"asdf://stsci.edu/datamodels/roman/manifests/datamodels-{latest_version}"

    # Only need to worry about the tagged objects so the manifest will tell us the latest schema URIs
    for entry in asdf.schema.load_schema(datamodels_uri)["tags"]:
        yield entry["schema_uri"]

    # Now find the latest SSC schema URIs
    with asdf_ssc_config() as config:
        for uri in config.resource_manager:
            if uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/SSC"):
                yield uri


def _process(verbose: bool = False) -> ArchiveOutput:
    super_schemas: dict[Path, dict[str, Any]] = {}
    archive_schemas: dict[str, dict[str, Any]] = {}
    archive_data: list[str] = []

    for uri in _get_latest_uris():
        schema = super_schema(uri)
        if verbose:
            print(f"    processing {uri}")
        if "datamodel_name" in schema:
            if verbose:
                print("        -> datamodel super_schema")
            path = Path(uri.replace("asdf://stsci.edu/datamodels/roman/schemas/", "")).with_suffix(".yaml")
            super_schemas[path] = schema

        if "archive_meta" in schema:
            if verbose:
                print("        -> archive information")
            archive_schemas[uri] = archive_schema(schema)
            archive_data.extend(archive_entries(schema))

    return {
        "super_schemas": super_schemas,
        "archive_schemas": archive_schemas,
        "archive_data": archive_data,
    }


def dump(
    base_dir: Path,
    super_schema: bool = True,
    archive_json: bool = True,
    archive_yaml: bool = True,
    archive_txt: bool = True,
    verbose: bool = False,
) -> ArchiveOutput:
    output = _process(verbose=verbose)

    base_dir.mkdir(parents=True, exist_ok=True)

    if super_schema:
        super_dir = base_dir / "super_schemas"
        for path, schema in output["super_schemas"].items():
            save_path = super_dir / path
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with save_path.open("w") as f:
                yaml.dump(schema, f, sort_keys=True)

    if archive_json:
        with (base_dir / "archive_schemas.json").open("w") as f:
            json.dump(output["archive_schemas"], f)

    if archive_yaml:
        with (base_dir / "archive_schemas.yaml").open("w") as f:
            yaml.dump(output["archive_schemas"], f, sort_keys=True)

    if archive_txt:
        with (base_dir / "archive_data.txt").open("w") as f:
            f.write("\n".join(output["archive_data"]))

    return output
