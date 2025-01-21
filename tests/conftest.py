import asdf
import pytest
import yaml

MANIFEST_URIS = [
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0",
]
MANIFESTS = [yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS]


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param
