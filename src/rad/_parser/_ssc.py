from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import files
from typing import TYPE_CHECKING

import asdf
import asdf.resource
import asdf.schema

from rad import resources

if TYPE_CHECKING:
    from collections.abc import Generator


__all__ = ["asdf_ssc_config"]


@contextmanager
def asdf_ssc_config() -> Generator[asdf.config.AsdfConfig, None, None]:
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
