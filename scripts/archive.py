from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path

import asdf
import asdf.schema
import yaml

from rad import resources
from rad._super_schema import archive_data, archive_schema, super_schema

latest_dir = Path(__file__).parent.parent.absolute() / "latest"
latest_uris = (yaml.safe_load(latest_path.read_bytes())["id"] for latest_path in latest_dir.glob("**/*.yaml"))


@contextmanager
def asdf_ssc_config():
    """
    Fixture to load the SSC schemas into asdf for testing
    """
    with asdf.config_context() as config:
        resource_mapping = asdf.resource.DirectoryResourceMapping(
            files(resources) / "schemas" / "SSC", "asdf://stsci.edu/datamodels/roman/schemas/SSC/", recursive=True
        )
        config.add_resource_mapping(resource_mapping)

        yield config

    # Clear the schema cache to avoid issues with other tests
    #   ASDF normally caches the loaded schemas so they don't have to be reloaded
    #   but this creates a problem for the asdf-pytest-plugin, if those tests
    #   are run after these tests because the loaded schemas will then be cached
    #   and not fail. But if they are run before these tests then asdf-pytest-plugin
    #   will fail because the references cannot be resolved through ASDF.
    asdf.schema._load_schema_cached.cache_clear()


if __name__ == "__main__":
    with asdf_ssc_config():
        archive_uris = {}
        archive_entries = []
        for uri in latest_uris:
            if uri == "asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0":
                continue

            print(f"Processing {uri}")
            schema = super_schema(uri)
            if "archive_meta" in schema:
                print("    -> archive product")
                archive_uris[uri] = archive_schema(schema)
                archive_entries.extend(archive_data(schema))

    with open("archive_schemas.yaml", "w") as f:
        yaml.dump(archive_uris, f, sort_keys=True)

    with open("archive_strings.txt", "w") as f:
        f.write("\n".join(archive_entries))
