import asdf
import pytest
import yaml

MANIFEST = yaml.safe_load(asdf.get_config().resource_manager["asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"])


@pytest.fixture(scope="session")
def manifest():
    return MANIFEST
