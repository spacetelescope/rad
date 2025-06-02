"""
Tool to generate catalog schemas from a csv describing columns.
"""

import argparse
import csv
import pathlib

catalogs = {
    "forced": {
        "header": {
            "schema_id": "forced_catalog_table-1.0.0",
            "title": "Forced source catalog table schema",
        },
    },
    "prompt": {
        "header": {
            "schema_id": "prompt_catalog_table-1.0.0",
            "title": "Prompt source catalog table schema",
        },
    },
    "multiband": {
        "header": {
            "schema_id": "multiband_catalog_table-1.0.0",
            "title": "Multiband source catalog table schema",
        },
    },
}

header = """%YAML 1.1
---
$schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
id: asdf://stsci.edu/datamodels/roman/schemas/{schema_id}

title: {title}

type: object
properties:
  columns:
    allOf:"""

template = """
      - not:
          items:
            not:
              description: {description}
              unit: {unit}
              properties:
                name:
                  pattern: {pattern}
                data:
                  properties:
                    datatype:
                      enum: [{dtype}]"""

footer = """
"""

BAND_NAMES = ("f062", "f087", "f106", "f129", "f158", "f184", "f213", "f146")
BAND_REGEX = "(" + "|".join(BAND_NAMES) + ")"
BAND_OR_NONE_REGEX = "(|" + "|".join(f"_{band}" for band in BAND_NAMES) + ")"
RADIUS_REGEX = "[0-9]{2}"


class Column:
    @classmethod
    def from_row(cls, row):
        column = cls()
        column.name = row["Name"].strip()
        column.cat_types = set()
        if row["Prompt"].strip().upper() == "Y":
            column.cat_types.add("prompt")
            # prompt and forced contain the same columns just with some renaming
            column.cat_types.add("forced")
        column.forced = bool(row["Forced"].strip().upper())
        if row["Multiband"].strip().upper() == "Y":
            column.cat_types.add("multiband")
        column.dtype = row["Type"].strip()
        if column.dtype == "boolean":
            column.dtype = "bool8"
        column.unit = row["Unit"].strip() or "none"
        if not isinstance(column.unit, str):
            column.unit = "none"
        column.description = row["Description"].strip().replace("\n", " ")
        return column

    def is_included(self, cat_type):
        return cat_type in self.cat_types

    def pattern(self, cat_type):
        pattern = self.name

        # format based on catalog type
        if cat_type in ("prompt", "forced"):
            pattern = pattern.replace("_<band>", "")

        if cat_type == "multiband":
            pattern = pattern.replace("<band>", BAND_REGEX)

        if cat_type == "forced" and self.forced:
            pattern = f"forced_{pattern}"

        if "<radius>" in pattern:
            pattern = pattern.replace("<radius>", RADIUS_REGEX)
        return f"^{pattern}$"

    def render(self, cat_type):
        return template.format(
            dtype=self.dtype,
            unit=self.unit,
            pattern=self.pattern(cat_type),
            description=self.description,
        )


def generate_schemas(csv_fn, output_dir):
    output_dir = pathlib.Path(output_dir)

    with open(csv_fn) as f:
        reader = csv.DictReader(f)
        columns = [Column.from_row(row) for row in reader]

    for name, meta in catalogs.items():
        schema = header.format(**meta["header"])
        for column in columns:
            if column.is_included(name):
                schema += column.render(name)
        schema += footer

        schema_fn = f"{name}_catalog_table.yaml"

        with open(output_dir / schema_fn, "w") as f:
            f.write(schema)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Source catalog schema generator")
    parser.add_argument("csv_filename")
    parser.add_argument("-o", "--output_directory", default=".")
    args = parser.parse_args()

    generate_schemas(args.csv_filename, args.output_directory)
