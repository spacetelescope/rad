import importlib.resources as importlib_resources

from asdf.resource import DirectoryResourceMapping


class RadDirectoryResourceMapping(DirectoryResourceMapping):
    """
    A Custom DirectoryResourceMapping that avoids the SSC schemas.

    Note:
        DirectryResourceMapping uses fnmatch on the file's name not its full path
        so it is not easy to exclude the files from the SSC directory using the
        filename_pattern argument. So we override the _iterate_files method to
        filter out any files in the SSC directory.
    """

    def _iterate_files(self, directory, path_components):
        for file, components in super()._iterate_files(directory, path_components):
            if "SSC" not in str(file):
                yield file, components


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
        RadDirectoryResourceMapping(resources_root / "schemas", "asdf://stsci.edu/datamodels/roman/schemas/", recursive=True),
        DirectoryResourceMapping(resources_root / "manifests", "asdf://stsci.edu/datamodels/roman/manifests/"),
    ]
