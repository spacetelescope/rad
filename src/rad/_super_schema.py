from __future__ import annotations

import copy
import functools
from collections import abc
from typing import TYPE_CHECKING

import asdf.schema
import asdf.treeutil

if TYPE_CHECKING:
    from typing import Any


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
        schema.pop("required", None)
        schema.pop("type", None)
        schema.pop("anyOf", None)
        schema.pop("additionalProperties", None)
        schema.pop("$schema", None)
        schema.pop("flowStyle", None)
        schema.pop("propertyOrder", None)
        schema.pop("datamodel_name", None)

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
            new_node = {"archive_catalog": schema["archive_catalog"]}
            if "title" in schema:
                new_node["title"] = schema["title"]
            if "description" in schema:
                new_node["description"] = schema["description"]
            return new_node
        else:
            return None

    return schema
