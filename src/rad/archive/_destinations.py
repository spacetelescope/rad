from dataclasses import dataclass
from itertools import chain
from sys import version_info

if version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources

import yaml
from flatten_dict import flatten, unflatten

from rad import resources

SCHEMAS = list((importlib_resources.files(resources) / "schemas").glob("**/*.yaml"))
IGNORED_SCHEMAS = list((importlib_resources.files(resources) / "schemas").glob("**/rad_schema*.yaml"))
DESTINATION_KEYS = ["archive_catalog", "destination"]
DATATYPE_KEYS = ["archive_catalog", "datatype"]


@dataclass
class ArchiveData:
    destination: list = None
    datatype: str = None
    schema_name: str = None
    schema_path: str = None

    @property
    def _destination(self):
        if self.destination is not None:
            return tuple(zip(*[dest.split(".") for dest in self.destination]))

        return None, None

    @property
    def table_name(self):
        return self._destination[0]

    @property
    def field_name(self):
        return self._destination[1]

    def add_destination(self, destination: str):
        if self.destination is None:
            self.destination = []

        self.destination.append(destination)

    def add_datatype(self, datatype: str):
        if self.datatype is not None:
            raise ValueError(f"Datatype already set to {self.datatype}!\nCan not set as {datatype}.")

        self.datatype = datatype


def _load_schema(path) -> dict:
    """Load a flattened schema"""
    with path.open() as f:
        return flatten(yaml.safe_load(f), reducer="tuple", enumerate_types=(list,))


def _search_keys(schema: dict, keys: list) -> dict:
    """Search for a list of keys in a flattened schema"""
    for key in keys:
        schema = {key_: value for key_, value in schema.items() if key in key_}

    return schema


def _destination(schema: dict) -> dict:
    """Parse the schema down to the only the destination data"""

    fixed = {}
    # _search_keys, parses schema down to only the destination data
    # This loop turns the destination data into a dictionary of ArchiveData objects
    # and fixes the over-zealous flattening of the schema's lists (destination is a list)
    for key, value in _search_keys(schema, DESTINATION_KEYS).items():
        # All destination information should be a list which gets turned into an
        # integer-keyed dictionary by flatten_dict. This checks if the last key is an integer
        # and raises an error if it is not (indicating that the schema is not formatted correctly)
        if isinstance(key[-1], int):
            new_key = key[:-2]  # Remove the integer and "destination" from the key tuple

            # Create/extend the ArchiveData object
            if new_key in fixed:
                fixed[new_key].add_destination(value)
            else:
                fixed[new_key] = ArchiveData(destination=[value])

        else:
            raise RuntimeError(f"Destinations should be a list, {key} is not pointing to a list.")

    return fixed


def _datatypes(schema: dict) -> dict:
    """
    Parse the schema down to the only the datatype data.

    This will be appended to the destination data's ArchiveData objects.
    """
    return _search_keys(schema, DATATYPE_KEYS)


def _combine_data(schema: dict) -> dict:
    """
    Pull and combine the destination and datatype data into a single dictionary of ArchiveData objects.
    """
    # Pull destination data first as it will be a dictionary of ArchiveData objects
    data = _destination(schema)

    # Combine the datatype data into the ArchiveData objects
    for key, value in _datatypes(schema).items():
        new_key = key[:-1]

        if new_key in data:
            data[new_key].add_datatype(value)
        else:
            data[new_key] = ArchiveData(datatype=value)

    return data


def _archive_data(path) -> dict:
    """
    Create a dictionary of ArchiveData objects from a schema file.

    This also fills in all the data not related to the destination or datatype.
    """
    name = path.name
    data = _combine_data(_load_schema(path))  # Pull the destination and datatype data from the schema

    # Transform dictionary keys into "dot" separated keys
    data = flatten(unflatten(data, splitter="tuple"), reducer="dot", enumerate_types=(list,))

    # Fill in the ArchiveData objects with the rest of the data
    for key, value in data.items():
        value.schema_name = name
        value.schema_path = key

    return data


def archive_data() -> dict:
    """
    Find and collect all the archive data from all the schemas.
    """

    return list(
        chain.from_iterable(_archive_data(schema).values() for schema in sorted(SCHEMAS) if schema not in IGNORED_SCHEMAS)
    )
