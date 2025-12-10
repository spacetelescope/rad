from __future__ import annotations

import copy
from collections import abc
from typing import TYPE_CHECKING
from urllib.parse import urldefrag

import asdf
import asdf.schema
import asdf.treeutil
from asdf.generic_io import resolve_uri

if TYPE_CHECKING:
    from typing import Any


__all__ = ["super_schema"]


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
            suburl_base, suburl_fragment = urldefrag(resolve_uri(json_id, node["$ref"]))

            if suburl_base == schema_uri or suburl_base == schema.get("id"):
                # This is a local ref, which we'll resolve in both cases.
                subschema = schema
            else:
                subschema = asdf.schema.load_schema(suburl_base, resolve_references=True)

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
                # special case for datamodel_name to allow CCSP derived products
                if key != "datamodel_name":
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
        if isinstance(node, abc.Mapping) and "allOf" in node:
            # Special case for table columns, we want them to remain in the super schema
            # for display purposes, but remove the allOf combiner as it cannot be merged
            # easily. This is fine as the super schema is not used for validation. Only
            # for informational reference.
            if "not" in node["allOf"][0]:
                node["all_of_columns"] = node["allOf"]
                del node["allOf"]
                return node

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
