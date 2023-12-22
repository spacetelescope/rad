import sys

from asdf.resource import DirectoryResourceMapping

if sys.version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources


class RadResourceMapping(DirectoryResourceMapping):
    @property
    def root(self):
        return self._root

    @property
    def uri_prefix(self):
        return self._uri_prefix

    def get_file_path(self, uri):
        return self._uri_to_file[uri]


def get_resource_mappings():
    """
    Get the resource mapping instances for the datamodel schemas
    and manifests.  This method is registered with the
    asdf.resource_mappings entry point.

    Returns
    -------
    list of collections.abc.Mapping
    """
    from . import resources

    resources_root = importlib_resources.files(resources)

    return [
        RadResourceMapping(resources_root / "schemas", "asdf://stsci.edu/datamodels/roman/schemas/", recursive=True),
        RadResourceMapping(resources_root / "manifests", "asdf://stsci.edu/datamodels/roman/manifests/"),
        RadResourceMapping(resources_root / "meta_schemas", "asdf://stsci.edu/datamodels/roman/meta_schemas/"),
    ]
