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


@pytest.fixture(scope="session")
def l2_schema():
    return asdf.schema.load_schema(_L2_SCHEMA_PATH, resolve_references=True)


@pytest.fixture()
def subschema(l2_schema, request):
    path = request.param
    schema = l2_schema
    if not path:
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


@pytest.mark.parametrize("subschema", ["data"], indirect=True)
def test_data(subschema):
    assert subschema["datatype"] == "float32"
    assert subschema["exact_datatype"]
    assert subschema["ndim"] == 2


@pytest.mark.parametrize("subschema", ["dq"], indirect=True)
def test_dq(subschema):
    assert subschema["datatype"] == "uint32"
    assert subschema["exact_datatype"]
    assert subschema["ndim"] == 2


@pytest.mark.parametrize("subschema", ["meta.filename"], indirect=True)
def test_meta_filename(subschema):
    assert subschema["type"] == "string"


@pytest.mark.parametrize("subschema", ["meta.observation.execution_plan"], indirect=True)
def test_meta_observation_execution_plan(subschema):
    assert subschema["type"] == "integer"


@pytest.mark.parametrize("subschema", ["meta.observation.segment"], indirect=True)
def test_meta_observation_segment(subschema):
    assert subschema["type"] == "integer"


@pytest.mark.parametrize("subschema", ["meta.observation.program"], indirect=True)
def test_meta_observation_program(subschema):
    assert subschema["type"] == "integer"


@pytest.mark.parametrize("subschema", ["meta.observation.pass"], indirect=True)
def test_meta_observation_pass(subschema):
    assert subschema["type"] == "integer"


@pytest.mark.parametrize("subschema", ["meta.observation.exposure"], indirect=True)
def test_meta_observation_exposure(subschema):
    assert subschema["type"] == "integer"


@pytest.mark.parametrize("subschema", ["meta.observation.visit"], indirect=True)
def test_meta_observation_visit(subschema):
    assert subschema["type"] == "integer"


@pytest.mark.parametrize("subschema", ["meta.instrument.detector"], indirect=True)
def test_meta_instrument_detector(subschema):
    assert _find_key(subschema, "type") == "string"
    assert set(_find_key(subschema, "enum")) == set([f"WFI{i:02}" for i in range(1, 19)])


@pytest.mark.parametrize("subschema", ["meta.instrument.optical_element"], indirect=True)
def test_meta_instrument_optical_element(subschema):
    assert _find_key(subschema, "type") == "string"
    assert set(_find_key(subschema, "enum")) == {
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
    }


@pytest.mark.parametrize("subschema", ["meta.exposure.start_time"], indirect=True)
def test_meta_exposure_start_time(subschema):
    assert subschema["tag"] == "tag:stsci.edu:asdf/time/time-1.*"


@pytest.mark.parametrize(
    "subschema, required",
    [
        ("", {"data", "dq"}),
        ("meta", {"filename"}),
        ("meta.observation", {"execution_plan", "segment", "program", "pass", "exposure"}),
        ("meta.instrument", {"detector", "optical_element"}),
        ("meta.exposure", {"start_time"}),
    ],
    indirect=["subschema"],
)
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
