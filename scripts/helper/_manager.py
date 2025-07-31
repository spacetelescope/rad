"""
This module define's the app's handling of the collection of RAD resources
--> The result is a Textual DirectoryTree that can be used to display the resources
    and manage them through the app.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Protocol

from rich.style import Style
from rich.text import Text
from textual.messages import Message
from textual.widgets import DirectoryTree

from ._bump import Bump
from ._frozen import frozen_uris
from ._resource import Resource
from ._screen import BumpScreen, NewScreen

__all__ = ("Manager",)


class _Manager:
    """
    A class to manage the collection of RAD resources and provide methods for working with them.
    ---> This is a pseudo-Mapping class, it does not inherit from Mapping simply because of
         annoying issues with metaclass conflicts with Textual. The main usage of this class's
         Mapping-like behavior is simply the [] (__getitem__) operation to retrieve resources

    ---> The manager holds the actual resources in the
            _resources: dict[str, Resource]
        variable, which is a mapping of the resource URI (id: in yaml files) to a Resource object.
    ---> For convenience of access there is also the
            _key_map: dict[str | Path, str]
        variable, which maps Paths or strings (URIs) to a resource URI. Which is used so that
        the manager can find a resource by its path or URI without needing to have a different
        access path for each type of key.
    ---> The manager also holds a set of URI strings that are correspond to the "frozen/locked"
        Resources which are those that cannot be updated or changed due to their public release
        status. Hence the need for "version bumping" in the first place. This set should not
        change throughout the lifetime of the manager, as it is assumed that no release will
        occur while the manager is in use.

    Parameters
    ----------
    path : Path
        The path to the RAD repository (the resources directory will be `path/latest`).
    resources : dict[str, Resource] | None, optional
        A dictionary of resources to initialize the manager with, by default None
    key_map : dict[str | Path, str] | None, optional
        A mapping of paths or URIs to resource URIs, by default None
    frozen : frozenset[str] | None, optional
        A frozenset (immutable set) of URIs that are considered frozen resources. When
        the frozen parameter is not provided, it will automatically be generated
        from the Git repository located at `path`. This process is quite slow because
        it requires going through the Git history and reading files out of it and then
        finding the URIs in those files. Hence, it should only be created once.
    """

    def __init__(
        self,
        path: Path,
        *,
        resources: dict[str, Resource] | None = None,
        key_map: dict[str | Path, str] | None = None,
        frozen: frozenset[str] | None = None,
    ) -> None:
        self._repository = path
        self._resources = resources or {}
        self._key_map = key_map or {}

        self._frozen = frozen or frozen_uris(path)
        self._walk_resources()

    def __getitem__(self, item: Path | str) -> Resource:
        """
        Get the resource for the given item
        --> Item is either the path to the resource or the resource's URI
        """
        return self._resources[self._get_path(item)]

    def init_bump(self, path: Path | str) -> Bump:
        """
        Initialize a Bump object for the given path
        --> Path not uri is used because the Manager as a DirectoryTree will be
            outputting things in terms of paths, not URIs.
        --> The Bump object will be what handles the actual version bumping process

        Parameters
        ----------
        path : Path | str
            The path to the resource to bump.

        Returns
        -------
        Bump
            A Bump object that contains the resource and a generator for the resources
        """
        return Bump(self[path], self._resources_to_update(path))

    def bump(self, generator: Generator[Resource | None, None, None]) -> None:
        """
        Execute the bump process on the resources provided by the generator or
        reset the resources if no bumping is needed
        """
        for resource in generator:
            # The Reset process is done inside the generator and returns None
            if resource is not None:
                self._update_resource(resource)

    @property
    def repository(self) -> Path:
        """
        Get the path to the RAD repository.
        --> This is the path where the resources are stored and managed.

        Returns
        -------
        Path
            The path to the RAD repository.
        """
        return self._repository

    @property
    def unsaved_path(self) -> Path:
        """
        Get the path to the unsaved modifications directory.
        --> This is where the app will save any unsaved modifications to resources
            that are not yet committed to the repository.

        Returns
        -------
        Path
            The path to the unsaved modifications directory.
        """
        path = self._repository / "unsaved_modifications"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def prefixes(self) -> set[str]:
        """
        Get the prefixes for the resources in the manager.
        --> This is used to determine the prefixes for the resources in the
            DirectoryTree widget.

        Returns
        -------
        set[str]
            A set of prefixes for the resources in the manager.
        """
        return {resource.prefix for resource in self._resources.values()} | {uri.split("-")[0] for uri in self._frozen}

    @property
    def datamodels_manifest(self) -> Resource:
        """
        Get the datamodels manifest resource.
        --> This is a special resource that contains the manifest of all the
            datamodels in the RAD repository.

        Returns
        -------
        Resource
            The datamodels manifest resource.
        """
        manifests = [
            resource for resource in self._resources.values() if resource.is_manifest and "manifests/datamodels" in resource.uri
        ]
        if len(manifests) != 1:
            raise RuntimeError("Found more than one datamodels manifest resource.")

        return manifests[0]

    def _add_resource(self, item: Path | Resource) -> None:
        """
        Add a resource to the manager.
        --> It can be either a Resource object itself or a Path to a resource, which
            will then be read into a Resource object.

        Parameters
        ----------
        item : Path | Resource
            The resource to add, either as a Resource object or a Path to a resource file.

        Effect
        ------
        Adds (and may create it too) the resource to the manager
        """
        # Create the resource object if it is not already one
        resource = item if isinstance(item, Resource) else Resource.from_path(item, self._repository)

        # Check the resource against the frozen
        # --> Cannot be done in the Resource itself because it has no knowledge
        #     of the frozen resources itself. Hence, the external update here
        if resource.uri in self._frozen:
            resource.frozen = True

        # Add the resource to the manager's resources
        self._resources[resource.uri] = resource

        # Add to the key map for uri/path lookups
        self._key_map[resource.uri] = resource.uri
        self._key_map[resource.path] = resource.uri

    def _get_path(self, item: Path | str) -> str:
        """
        Turn a Path or URI into a resource URI.
        --> Will try to add a resource to the manager if there isn't one already
            there

        Parameters
        ----------
        item : Path | str
            The path or URI to the resource.

        Effects
        -------
        - Add a new resource to the manager if it is not already present.
        - Return the URI of the resource.
        """
        # Create add the resource to the manager if necessary
        if item not in self._key_map and isinstance(item, Path):
            self._add_resource(item)

        # Return the uri for the resource
        return self._key_map[item]

    def _remove_resource(self, resource: Resource) -> None:
        """
        Remove the resource from the manager.

        Parameters
        ----------
        resource : Resource
            The resource to remove from the manager.

        Effect
        ------
        Removes the resource from the manager
        """
        del self._key_map[resource.uri]
        del self._key_map[resource.path]
        del self._resources[resource.uri]

    def _update_resource(self, new_resource: Resource) -> None:
        """
        Update an existing resource in the manager with a new version of it

        Parameters
        ----------
        new_resource : Resource
            The new resource to update the existing one with.

        Effects
        -------
        - Updates the existing resource with the new one.
        - Updates all the resources under management that reference the old resource's URIs
          to be consistent with the new resource's URIs. (Apply the cacade of URI updates)
          --> This is the reason why we need to order the bumps according to the topological
              sort of the dependent resources, so that a new resource from Bump will not
              override the existing modifications made in this method
        """
        # Get the current resource from the manager
        current_resource = self[new_resource.path]

        # Error checking, we expect the new resource to be a different version
        # so its URI should not match the current resource's URI
        if current_resource.uri == new_resource.uri:
            raise RuntimeError("Attempting to update a resource with the same URI.")

        # Remove the current resource from the manager and add the new one
        self._remove_resource(current_resource)
        self._add_resource(new_resource)

        # Update the URIs related to the new resource throughout the manager
        self._update_uri(current_resource.uri, new_resource.uri)
        self._update_uri(current_resource.tag_uri, new_resource.tag_uri)

    def _update_uri(self, current_uri: str, new_uri: str) -> None:
        """
        Performs an update to the resources in the manager that have a reference
        to the current URI and replaces it with the new URI.

        Parameters
        ----------
        current_uri : str
            The current URI to update from.
        new_uri : str
            The new URI to update to.

        Effect
        ------
        Updates all resources in the manager that reference the current URI to the new one.
        """
        for resource in self._resources.values():
            # Only update the resources that currently reference the URI in their body
            if current_uri in resource.body:
                # Check to make sure that the resource is not frozen
                # --> Something has gone wrong if we are trying to update a frozen resource
                if resource.frozen:
                    raise RuntimeError("Attempting to update a frozen resource.")

                # Run the update on the resource
                new_resource = resource.update_uri(current_uri, new_uri)

                # Check that we have not changed the URI between new_resource
                # and the old one. This change should be happening prior to this
                # method being called. Meaning that something has gone wrong
                # if the URIs do not match
                if new_resource.uri != resource.uri:
                    raise RuntimeError("This method should not be used to change the URI of a resource.")

                # Update the resource in the manager
                self._resources[new_resource.uri] = new_resource

    def add_tag_entry(self, entry: str) -> None:
        """
        Add a tag entry to the resource's tag URI.
        --> This is used to add a new tag entry to the resource's tag URI.

        Parameters
        ----------
        entry : str
            The tag entry to add to the resource's tag URI.
        """
        # Update the resource with the new tag entry
        new_manifest = self.datamodels_manifest.add_tag_entry(entry)

        if new_manifest.uri != self.datamodels_manifest.uri:
            raise RuntimeError("This method should not be used to change the URI of a manifest.")

        # Update the resource in the manager
        self._resources[new_manifest.uri] = new_manifest

    def _resources_to_update(self, path: Path | str) -> Generator[Bump, None, None]:
        """
        Generator for all the resources that need to be updated when the given path
        is updated.

        --> This works through the cascade of resources that need to be updated
            if a schema is updated via a recursive search through the resources

        Parameters
        ----------
        path : Path | str
            The path to the resource that is being updated.

        Yields
        ------
        Bump
            A Bump object for a resource that directly references the resource
            being bumped.
        """
        update = self[path]

        for resource in self._resources.values():
            if resource is update:
                continue

            if (update.uri in resource.body or update.tag_uri in resource.body) and resource.frozen:
                yield Bump(resource, self._resources_to_update(resource.path))

    def _walk_resources(self) -> None:
        """
        Walk through the resources in the repository and add them to the manager.
        --> This is used to initialize the manager with the resources in the repository.
        """
        for path in (self._repository / "latest").glob("**/*.yaml"):
            self._add_resource(path)


class Manager(_Manager, DirectoryTree):
    """
    The Textual wrapper for the RAD resources manager.
    ---> This is an extension of the Textual DirectoryTree widget, which provides
         a nice interface for displaying and interacting with directories and files.

    Note
    ----
    The DirectoryTree App is not great about updating the tree when file modifications
    are made outside of the app. Hence, users should not expect the tree to reflect
    changes they made outside of the app. Instead they should close the app and
    re-open it to see the external changes.
    """

    ICON_LOCKED = "🔒"

    class Complete(Message):
        """
        Message to be issued with a bump operation is complete.
        """

        def __init__(self, state: BumpScreen.Return) -> None:
            super().__init__()
            self.state = state

    def __init__(
        self,
        path: Path,
        *,
        resources: dict[str, Resource] | None = None,
        key_map: dict[str | Path, str] | None = None,
        frozen: set[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(path, resources=resources, key_map=key_map, frozen=frozen)
        # Note here we are passing the `path / "latest"` to the DirectoryTree
        #   so that it will only capture the latest resources directory which is
        #   where the resources should be edited and managed.
        # Note that the `_resources` will be populated by the `filter_paths` method
        #   when the DirectoryTree is displayed, which happens when the app displays
        #   its main screen.
        super(_Manager, self).__init__(path / "latest", **kwargs)

    def filter_paths(self, paths: Iterable[Path]) -> Generator[Path, None, None]:
        """
        Filter the paths that the tree view will display to only include the directories
        and YAML files that are RAD resources.

        Note
        ----
        This method is what allows the custom DirectoryTre to render as we want
        it to and make sure that it "knows" about the RAD resources it is displaying.

        Parameters
        ----------
        paths : Iterable[Path]
            The paths to filter.

        Yields
        ------
        Path
            The paths that are directories or YAML files that are RAD resources.

        Effect
        ------
        If a path is a rad resource, it will construct the corresponding Resource
        object and add it to the manager
        """
        for path in paths:
            if path.is_dir():
                # If the path is a directory, yield it directly
                yield path

            elif path.suffix == ".yaml":
                # Note that the call to self[path] will ensure that the resource
                # is added to the resources if it is not already present.
                yield self[path].path
                # yield path

    def render_label(self, node: _DirEntry, base_style: Style, style: Style) -> Text:
        """
        Modify the label of the node to indicate if it is frozen with a "🔒" symbol
        """
        path = node.data.path  # Get the path information from the node data

        # Store the original icon file to restore later
        base_icon = self.ICON_FILE

        # Safety check to ensure we are dealing with a RAD resource
        if path.is_file() and path.suffix == ".yaml":
            # Check if the resource is frozen and if so, override the icon
            # with the locked icon
            if self[path].frozen:
                self.ICON_FILE = self.ICON_LOCKED

        # Render the label using the original render_label_method
        #   this uses the `self.ICON_FILE` to set the icon in the text
        #   hence why we override it above for frozen resources
        text = super().render_label(node, base_style, style)

        # Restore the original icon file after rendering
        #   this is important to ensure that the next node
        #   does not inherit the locked icon if it is not frozen
        self.ICON_FILE = base_icon

        return text

    def bump(self, state: BumpScreen.Return, generator: Generator[Resource | None, None, None]) -> None:
        """
        Add in the Textual message to the bump process to indicate a successful bump
        """
        super().bump(generator)

        # Notify the user of the result
        match state:
            case BumpScreen.Return.BUMP:
                self.notify("Resources bumped successfully.", severity="success")
            case BumpScreen.Return.RETURN:
                self.notify("Returned to main menu without bumping.", severity="info")
            case _:
                raise RuntimeError("Something went seriously wrong while bumping the resources.")

        self.post_message(self.Complete(state))

    def add_new_resource(self, state: NewScreen.Return, resource: Resource) -> None:
        """
        Add a new resource to the manager and the directory tree.
        --> This is used when a new resource is created in the app.

        Parameters
        ----------
        resource : Resource
            The new resource to add to the manager and the directory tree.
        """
        self._add_resource(resource)
        self.notify(f"New resource {resource.uri} added successfully.", severity="success")
        self.post_message(self.Complete(state))

    def edit_resource(self, edited_resource: Resource) -> None:
        """
        Edit the given resource in the app.
        --> This is used when a resource is edited in the app.

        Parameters
        ----------
        edited_resource : Resource
            The resource to edit.
        """
        current_resource = self[edited_resource.path]

        uri = edited_resource.uri
        tag_uri = edited_resource.tag_uri

        edited_resource = (
            edited_resource.update_uri(uri, current_resource.uri).update_uri(tag_uri, current_resource.tag_uri).overwrite()
        )

        # Remove the current resource from the manager and add the new one
        self._remove_resource(current_resource)
        self._add_resource(edited_resource)

        self.notify(f"Edit to {edited_resource.uri} successful.", severity="success")
        self.post_message(self.Complete(BumpScreen.Return.EDIT))


# Protocols for the node to render_label for DirctoryTree as
#   we make modifications to the label during rendering these
#   are "hidden" types in Textual, but they are constrained to
#   having `data` which contains the raw entry data and the
#   data has a `path` property because we are in a tree


class _DirData(Protocol):
    @property
    def path(self) -> Path: ...


class _DirEntry(Protocol):
    @property
    def data(self) -> _DirData: ...
