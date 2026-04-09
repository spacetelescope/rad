"""
These tests are to confirm that select metadata is required
and of a specific format in the L2 schemas.
The metadata tested is critical to the mission operations
center (MOC) pipelines and any changes need to be coordinated
with the MOC.

    roman/data
    roman/dq
    roman/meta/filename
    roman/meta/observation/execution_plan
    roman/meta/observation/segment
    roman/meta/observation/program
    roman/meta/observation/pass
    roman/meta/observation/exposure
    roman/meta/observation/visit
    roman/meta/instrument/detector
    roman/meta/instrument/optical_element
    roman/meta/exposure/start_time

The tests here largely duplicate the schema contents so
that the tests can check that the schemas are requiring
the expected types, structure, enums, etc.
"""

from pathlib import Path

import asdf
import pytest

_L2_SCHEMA_PATH = Path(__file__).parent.parent.absolute() / "latest" / "wfi_image.yaml"

TRUTH = {
    "data": {
        "datatype": "float32",
        "exact_datatype": True,
        "ndim": 2,
    },
    "dq": {
        "datatype": "uint32",
        "exact_datatype": True,
        "ndim": 2,
    },
    "meta.filename": {
        "type": "string",
    },
    "meta.observation.execution_plan": {
        "type": "integer",
    },
    "meta.observation.segment": {
        "type": "integer",
    },
    "meta.observation.program": {
        "type": "integer",
    },
    "meta.observation.pass": {
        "type": "integer",
    },
    "meta.observation.exposure": {
        "type": "integer",
    },
    "meta.observation.visit": {
        "type": "integer",
    },
    "meta.instrument.detector": {
        "type": "string",
        "enum": set([f"WFI{i:02}" for i in range(1, 19)]),
    },
    "meta.instrument.optical_element": {
        "type": "string",
        "enum": {
            "F062",
            "F087",
            "F106",
            "F129",
            "F146",
            "F158",
            "F184",
            "F213",
            "GRISM",
            "PRISM",
            "DARK",
            "NOT_CONFIGURED",
        },
    },
    "meta.exposure.start_time": {
        "tag": "tag:stsci.edu:asdf/time/time-1.*",
    },
}

REQUIRED = {
    "": {
        "data",
        "dq",
    },
    "meta": {
        "filename",
    },
    "meta.observation": {
        "execution_plan",
        "segment",
        "program",
        "pass",
        "exposure",
    },
    "meta.instrument": {
        "detector",
        "optical_element",
    },
    "meta.exposure": {
        "start_time",
    },
}


@pytest.fixture(scope="session")
def l2_schema():
    return asdf.schema.load_schema(_L2_SCHEMA_PATH, resolve_references=True)


@pytest.fixture()
def subschema(l2_schema, request):
    schema = l2_schema

    if not (path := request.param):
        return schema
    for subpath in path.split("."):
        if "allOf" in schema:
            # find sub schema with subpath
            queue = schema["allOf"].copy()
            while queue:
                subschema = queue.pop(0)
                if "allOf" in subschema:
                    queue.extend(subschema["allOf"])
                    continue
                if subpath in subschema["properties"]:
                    schema = subschema
                    break
        schema = schema["properties"][subpath]
    return schema


def _find_key(schema, key):
    values = []
    if key in schema:
        values.append(schema[key])
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            try:
                value = _find_key(subschema, key)
            except KeyError:
                continue
            values.append(value)
    if not values:
        raise KeyError(f"{key} not found")
    if len(values) > 1:
        raise ValueError(f"{key} maps to multiple values: {values}")
    return values[0]


@pytest.mark.parametrize("subschema, truth", TRUTH.items(), indirect=["subschema"])
def test_check_schema(subschema, truth):
    """Test that the schema matches the expected checks."""

    for key, value in truth.items():
        schema_value = _find_key(subschema, key)
        # Turn lists into sets for comparison
        if isinstance(value, set):
            schema_value = set(schema_value)

        assert schema_value == value

        # Check that boolean values are exactly the same
        if isinstance(value, bool):
            assert schema_value is value


@pytest.mark.parametrize("subschema, required", REQUIRED.items(), indirect=["subschema"])
def test_required(subschema, required):
    if "allOf" in subschema:
        schema_values = set()
        queue = subschema["allOf"].copy()
        while queue:
            sub = queue.pop(0)
            if "allOf" in sub:
                queue.extend(sub["allOf"])
                continue
            if "required" in sub:
                schema_values |= set(sub["required"])
    else:
        schema_values = set(subschema["required"])
    assert not (required - schema_values)
