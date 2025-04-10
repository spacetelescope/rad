import importlib.resources as importlib_resources

import yaml
from asdf.resource import DirectoryResourceMapping


class RadResourceMapping(DirectoryResourceMapping):
    def _make_uri(self, file, path_components):
        with file.open("rb") as f:
            yaml_file = yaml.safe_load(f.read())

        if "id" in yaml_file:
            return yaml_file["id"]

        return super()._make_uri(file, path_components)


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

    return [RadResourceMapping(resources_root, "", recursive=True)]
