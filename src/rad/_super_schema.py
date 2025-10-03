from __future__ import annotations

import copy
import functools
from collections import abc
from typing import TYPE_CHECKING

import asdf.schema
import asdf.treeutil

if TYPE_CHECKING:
    from typing import Any, TypedDict

    class ArchiveInfo(TypedDict):
        datatype: str
        destination: list[str]


@functools.cache
def _get_schema_from_uri(schema_uri: str) -> dict[str, Any]:
    """
    Load a schema from a URI, resolving all local references.

    Parameters
    ----------
    schema_uri : str
        The URI of the schema to load.

    Returns
    -------
    dict[str, Any]
        The loaded schema as a dictionary.
    """
    # See Issue https://github.com/asdf-format/asdf/issues/1977
    schema = asdf.schema.load_schema(schema_uri, resolve_references=False)

    def resolve_refs(node, json_id):
        if json_id is None:
            json_id = schema_uri

        if isinstance(node, dict) and "$ref" in node:
            suburl_base, suburl_fragment = asdf.schema._safe_resolve(None, json_id, node["$ref"])

            if suburl_base == schema_uri or suburl_base == schema.get("id"):
                # This is a local ref, which we'll resolve in both cases.
                subschema = schema
            else:
                subschema = asdf.schema.load_schema(suburl_base, None, True)

            return asdf.treeutil.walk_and_modify(asdf.reference.resolve_fragment(subschema, suburl_fragment), resolve_refs)

        return node

    return asdf.treeutil.walk_and_modify(schema, resolve_refs)


def _deep_merge(target: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    for key, value in source.items():
        if key in target:
            if isinstance(target[key], abc.Mapping):
                if not isinstance(value, abc.Mapping):
                    raise ValueError(f"Cannot merge non-mapping value {value} into {target[key]}")
                _deep_merge(target[key], value)
            elif isinstance(target[key], list) and isinstance(value, list) and key == "required":
                target[key] = list(set(target[key]) | set(value))
            elif key in ("title", "description"):
                target[key] += f"\n- {value}"
            elif target[key] != value:
                raise ValueError(f"{key} has conflicting values: {target[key]} and {value}")
        else:
            target[key] = value

    return target


def super_schema(schema_uri: str) -> dict[str, Any]:
    """
    Find the "super schema" for a given schema URI.
        -> Parse the schema URI and resolve the `allOf` combiners

    Parameters
    ----------
    schema_uri : str
        The URI of the schema to parse.

    Returns
    -------
    dict[str, Any]
        The parsed schema as a dictionary.
    """

    schema = _get_schema_from_uri(schema_uri)

    def callback(node: dict[str, Any]) -> dict[str, Any]:
        if isinstance(node, abc.Mapping) and "$schema" in node:
            del node["$schema"]
        if isinstance(node, abc.Mapping) and "id" in node:
            del node["id"]
        if isinstance(node, abc.Mapping) and "allOf" in node and "not" not in node["allOf"][0]:
            target = copy.deepcopy(node["allOf"][0])
            for item in node["allOf"][1:]:
                if isinstance(item, abc.Mapping):
                    item = copy.deepcopy(item)
                    if "$schema" in item:
                        del item["$schema"]
                    if "id" in item:
                        del item["id"]
                    target = _deep_merge(target, item)
                else:
                    raise ValueError(f"Expected a mapping in allOf, got {item}")

            del node["allOf"]
            return _deep_merge(node, target)
        return node

    id_ = schema.get("id")
    meta_ = schema.get("$schema")

    schema = asdf.treeutil.walk_and_modify(schema, callback)
    if id_:
        schema["id"] = id_
    if meta_:
        schema["$schema"] = meta_

    return schema


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


def archive_data(schema: dict[str, Any]) -> list[str]:
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
