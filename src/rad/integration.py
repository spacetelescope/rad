import importlib.resources as importlib_resources

from asdf.resource import DirectoryResourceMapping


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
        DirectoryResourceMapping(resources_root / "schemas", "asdf://stsci.edu/datamodels/roman/schemas/", recursive=True),
        DirectoryResourceMapping(resources_root / "manifests", "asdf://stsci.edu/datamodels/roman/manifests/"),
    ]
