import asdf
import pytest
import yaml

MANIFEST_URIS = [
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0",
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.1.0",
]
MANIFESTS = [yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS]
MANIFEST_ENTRIES = []
for manifest in MANIFESTS:
    MANIFEST_ENTRIES.extend(manifest["tags"])


@pytest.fixture(scope="session", params=MANIFEST_ENTRIES)
def manifest_entry(request):
    return request.param


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param
