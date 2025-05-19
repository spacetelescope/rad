import importlib.resources

import asdf
import yaml

from rad._source_catalogs import generate_schemas

CATALOG_CSV = importlib.resources.files("rad") / "resources" / "source_catalogs.csv"


def test_up_to_date_catalogs(tmp_path):
    generate_schemas(CATALOG_CSV, tmp_path)

    def error_msg(schema_id):
        return f"{schema_id} differs: regenerate the schemas with: python -m rad._source_catalogs docs/source_catalogs.csv -o latest/"

    # compare to latest/asdf resources
    resource_manager = asdf.get_config().resource_manager
    for fn in tmp_path.iterdir():
        with fn.open("rb") as f:
            generated_bytes = f.read()
            schema = yaml.safe_load(generated_bytes)
            resource = resource_manager[schema["id"]]
            assert resource == generated_bytes, error_msg(schema["id"])
