from itertools import chain
from sys import version_info

if version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources

import yaml
from flatten_dict import flatten

from rad import resources

SCHEMAS = list((importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
IGNORED_SCHEMAS = list((importlib_resources.files(resources) / "schemas").glob("**/rad_schema*.yaml"))
ARCHIVE_KEYS = ["archive_catalog", "destination"]


def _load_schema(schema) -> dict:
    with schema.open() as f:
        return flatten(yaml.safe_load(f), reducer="tuple", enumerate_types=(list,))


def _search_keys(schema: dict, keys: list) -> dict:
    for key in keys:
        schema = {key_: value for key_, value in schema.items() if key in key_}

    return schema


def destinations() -> list:
    """
    Returns a list of all archive destinations available in the schemas.
    """

    return sorted(
        chain.from_iterable(
            _search_keys(_load_schema(schema), ARCHIVE_KEYS).values() for schema in SCHEMAS if schema not in IGNORED_SCHEMAS
        )
    )
