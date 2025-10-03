from __future__ import annotations

import copy
from collections import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, TypedDict

    class ArchiveInfo(TypedDict):
        datatype: str
        destination: list[str]


__all__ = ["archive_entries", "archive_schema"]


def archive_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Process a schema for use by the MAST archive system.

    Parameters
    ----------
    schema : dict[str, Any]
        The schema to process.

    Returns
    -------
    dict[str, Any]
        The processed schema.
    """
    if isinstance(schema, abc.Mapping):
        new_schema = copy.deepcopy(schema)
        for key in schema:
            if key not in ("properties", "archive_catalog", "archive_meta"):
                new_schema.pop(key)

        schema = new_schema

    if isinstance(schema, abc.Mapping) and "properties" in schema:
        properties = {}
        for key, sub_node in schema["properties"].items():
            if new_node := archive_schema(sub_node):
                properties[key] = new_node

        if properties:
            schema["properties"] = properties
            return schema
        else:
            return {}

    if isinstance(schema, abc.Mapping):
        if "archive_catalog" in schema:
            return {"archive_catalog": schema["archive_catalog"]}
        else:
            return None

    return schema


def _flatten_dict(data: dict[str, Any], parent_key: str | None = None) -> dict[str, Any]:
    """
    Flatten a nested dictionary structure into a single-level dictionary.

    Parameters
    ----------
    d : dict[str, Any]
        The dictionary to flatten.
    parent_key : str, optional
        The parent key for the current recursion level, by default "".

    Returns
    -------
    dict[str, Any]
        A flattened dictionary where nested keys are joined with the separator.
    """
    parent_key = parent_key or ""

    items = []
    for key, value in data.items():
        new_key = f"{parent_key}.{key}" if parent_key else key

        if isinstance(value, abc.Mapping):
            items.extend(_flatten_dict(value, new_key).items())
        else:
            items.append((new_key, value))

    return dict(items)


def _path_archive(schema: dict[str, Any]) -> dict[str, ArchiveInfo]:
    """
    Produce a data path in schema to archive information mapping

    Parameters
    ----------
    schema : dict[str, Any]
        Schema to process

    Returns
    -------
    dict[str, Any]
        data-path: archive information
    """
    archive_filter = archive_schema(schema)
    archive_filter.pop("archive_meta")

    flat_schema = _flatten_dict(archive_filter)

    data = {}
    for key_path, value in flat_schema.items():
        base_path, archive_key = key_path.rsplit(".", 1)

        path = ".".join(
            item for item in base_path.split(".") if item != "properties" and item != "archive_catalog" and item != "meta"
        )

        if path not in data:
            data[path] = {}

        data[path][archive_key] = value

    return data


def _archive_string(path: str, datatype: str | None, destination: list[str]) -> list[str]:
    """
    Produce a string representation of an archive mapping

    Parameters
    ----------
    path : str
        Data path
    datatype : str | None
        Datatype of the data
    destination : list[str]

    Returns
    -------
    str
        String representation of the archive mapping
    """
    if len(path.split(".")) == 1:
        path = f"top.{path}"

    # Re append meta to the front of the path and add | to the end
    schema_path = f"meta.{path}|"

    # Last two components of the path, reversed and joined by |
    archive_path = "|".join(path.split(".")[-2:][::-1])

    if datatype is not None:
        if "char" in datatype.lower() or "str" in datatype.lower():
            schema_path = f"1||{schema_path}"
        else:
            schema_path = f"0||{schema_path}"

    return ["|".join([archive_path, *(dest.split(".")), schema_path]) for dest in destination]


def archive_entries(schema: dict[str, Any]) -> list[str]:
    """
    Produce a list of archive mapping strings from a schema

    Parameters
    ----------
    schema : dict[str, Any]
        Schema to process

    Returns
    -------
    list[str]
        List of archive mapping strings
    """
    archive_meta = schema.get("archive_meta")
    path_info = _path_archive(schema)

    archive_strings = []
    for path, archive_info in path_info.items():
        archive_strings.extend([f"{archive_meta}|{dest}" for dest in _archive_string(path, **archive_info)])

    return archive_strings
