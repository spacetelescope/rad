"""
This module defines the app's handling of individual RAD resources.
--> The result is a Textual widget that handles the resource's data and
    provides a user interface for bumping the resource's version.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from re import findall, sub
from shutil import copyfile
from textwrap import dedent, indent
from typing import Any, Self

from asdf.treeutil import walk_and_modify
from astropy.utils import lazyproperty
from rich.style import NULL_STYLE
from rich.text import Text
from semantic_version import Version
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.messages import Message
from textual.validation import ValidationResult, Validator
from textual.widgets import Input, Label
from yaml import safe_load

__all__ = ("Resource",)

_IGNORED_KEYWORDS = (
    "archive_meta",
    "archive_catalog",
    "sdf",
    "title",
    "description",
    "propertyOrder",
)


class _Resource:
    """
    This class handles the data for a single RAD resource.

    This performs several tasks:
    1. It reads (from_path) and stores all the information about a particular resource:
        - uri ("id:") field in the top level of the yaml file
        - path to the resource
        - (computes) the tag uri for the resource
        - (computes) the version of the resource
        - (computes) the symlink for the resource

    2. It provides methods to update the resource:
        - update_uri: finds and replaces a given uri with a new one
            - Used to update any URI reference in the resource to some new URI
        - bump: bumps the version of the resource
            - Updates the symlink's filename to reflect the new version
            - Copies the current resource to the (correct) resources directory under the old version
            - Updates the resource's URI to reflect the new version

    Parameters
    ----------
    uri : str
        The URI of the resource.
    path : Path
        The path to the resource.
    repository : Path
        The path to the RAD repository.
    body : str
        The body (text only) of the resource.
    frozen : bool
        Whether the resource is frozen or not.
    """

    URI_PREFIX = "asdf://stsci.edu/datamodels/roman/"
    SCHEMA_URI_PREFIX = f"{URI_PREFIX}schemas/"
    TAG_URI_PREFIX = f"{URI_PREFIX}tags/"
    MANIFEST_URI_PREFIX = f"{URI_PREFIX}manifests/"

    def __init__(self, uri: str, path: Path, repository: Path, body: str, frozen: bool) -> None:
        self.uri = uri
        self.path = path
        self.repository = repository
        self.body = body
        self.frozen = frozen

    @classmethod
    def from_path(cls, path: Path, repository: Path, *args, **kwargs) -> Self:
        """
        Construct the information about the resource from a path to the resource.
        """
        body = path.read_text()
        yaml = safe_load(body)
        uri = yaml["id"]

        return cls(uri, path, repository, body, False, *args, **kwargs)

    @classmethod
    def from_body(cls, body: str, repository: Path, *args, **kwargs) -> Self:
        """
        Construct the information about the resource from a body of text.
        """
        yaml = safe_load(body)
        uri = yaml["id"]

        # The URI is expected to be prefixed with either SCHEMA_URI_PREFIX or MANIFEST_URI_PREFIX
        # --> Remove each of those prefixes to get the correct uri_suffix
        # --> Remove the version suffix from the uri_suffix and then add the `.yaml` extension
        path = (
            repository
            / "latest"
            / f"{uri.split(cls.SCHEMA_URI_PREFIX)[-1].split(cls.MANIFEST_URI_PREFIX)[-1].split('-')[0]}.yaml"
        )

        return cls(uri, path, repository, body, False, *args, **kwargs)

    @classmethod
    def schema_from_uri_suffix(
        cls,
        uri_suffix: str,
        repository: Path,
        title: str,
        description: str,
    ) -> Self:
        """
        Create a schema resource from a URI, repository, and title.
        --> This is used to create a new resource, and should not be used on
            existing resources.

        Parameters
        ----------
        uri_suffix : str
            The URI suffix for the resource.
        repository : Path
            The path to the repository.
        title : str
            The title of the resource.
        description : str
            The description of the resource.

        Returns
        -------
        _Resource
            The created schema resource.
        """
        uri = f"{cls.SCHEMA_URI_PREFIX}{uri_suffix}"
        path = repository / "latest" / f"{uri_suffix.split('-')[0]}.yaml"

        body = dedent(
            f"""
            %YAML 1.1
            ---
            $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
            id: {uri}

            title: {title}
            """
        ).lstrip()

        # Only add the description if it is non-empty
        if description:
            body += dedent(
                f"""
                description: |-
                    {description.rstrip()}
                """
            )

        return cls(uri, path, repository, body, False)

    @classmethod
    def manifest_from_uri_suffix(cls, uri_suffix: str, repository: Path, title: str, description: str) -> Self:
        """
        Create a manifest resource from a URI, repository, and title.
        --> This is used to create a new resource, and should not be used on
            existing resources.

        Parameters
        ----------
        uri_suffix : str
            The URI suffix for the resource.
        repository : Path
            The path to the repository.
        title : str
            The title of the resource.
        description : str
            The description of the resource.

        Returns
        -------
        _Resource
            The created schema resource.
        """
        uri = f"{cls.MANIFEST_URI_PREFIX}{uri_suffix}"
        extension_uri = sub(r"manifests", r"extensions", uri)
        path = repository / "latest" / "manifests" / f"{uri_suffix.split('-')[0]}.yaml"

        body = dedent(
            f"""
            %YAML 1.1
            ---
            id: {uri}
            extension_uri: {extension_uri}
            asdf_standard_requirement:
              gte: 1.1.0

            title: {title}
            """
        ).lstrip()

        # Only add the description if it is non-empty
        if description:
            body += dedent(
                f"""
                description: |-
                    {description.rstrip()}
                """
            )

        body += dedent(
            """
            tags:
            """
        )

        return cls(uri, path, repository, body, False)

    @lazyproperty
    def tag_uri(self) -> str:
        """
        Get the tag URI for the resource.

        --> This may or may not actually be used in as part of the schemas, but
            it follows a pattern that all resources follow.

        --> The pattern is replace the `schemas` part of the URI with `tags`

        --> Tagged scalars are a weird special case, where the `/tagged_scalars`
            section of the URI is left out in all cases. So we need to process
            remove that section hence the split and join.

        --> Manifest files huse `extension_uri` instead of `tag_uri`, but there is
            no need to have a special uri case for that. The `tag_uri` is used
            --> Pattern is replace `manifests` with `extensions`

        """
        return sub(r"manifests", r"extensions", sub(r"schemas", r"tags", "".join(self.uri.split("/tagged_scalars"))))

    @lazyproperty
    def version(self) -> str:
        """
        Get the version of the schema.
        """
        return self.uri.split("-")[-1]

    @lazyproperty
    def prefix(self) -> str:
        """
        Get the prefix of the resource's URI.
        """
        return self.uri.split("-")[0]

    @lazyproperty
    def latest_path(self) -> Path:
        """
        Get the path to the latest version of the resource.
        """

        return self.repository / "latest"

    @lazyproperty
    def resources_path(self) -> Path:
        """
        Get the path to the resources directory.
        """
        return self.repository / "src" / "rad" / "resources"

    @lazyproperty
    def manifests_path(self) -> Path:
        """
        Get the path to the manifests directory.
        """
        return self.resources_path / "manifests"

    @lazyproperty
    def schemas_path(self) -> Path:
        """
        Get the path to the schemas directory.
        """
        return self.resources_path / "schemas"

    def _find_symlink_path(self, path: Path, version: str, uri: str) -> Path:
        """
        Find the symlink path given the current path, version, and uri.

        --> The symlink path is slightly different if the resource is a schema or a manifest.

        Parameters
        ----------
        path : Path
            The current path to the resource's true location.
        version : str
            The version of the resource. (used to determining the symlink name)
        uri : str
            The URI of the resource. (used to determine the type of resource)

        Returns
        -------
        Path
            The path to the symlink for the resource.
        """
        if "schemas" in uri:
            base_path = path.relative_to(self.latest_path)
        elif "manifest" in uri:
            base_path = path.relative_to(self.latest_path / "manifests")

        parent_path = base_path.parent
        filename = f"{base_path.stem}-{version}.yaml"

        # Determine the head of the symlink path
        if "schemas" in uri:
            return self.schemas_path / parent_path / filename
        elif "manifest" in uri:
            return self.manifests_path / parent_path / filename
        else:
            raise ValueError(f"Unknown resource URI: {uri}")

    @lazyproperty
    def symlink(self) -> Path:
        """
        Get the symlink for the resource.
        """
        return self._find_symlink_path(self.path, self.version, self.uri)

    @lazyproperty
    def symlink_target(self) -> Path:
        """
        Get the target of the symlink for the resource.
        """
        return self.path.relative_to(self.symlink.parent, walk_up=True)

    @lazyproperty
    def yaml(self) -> dict[str, Any]:
        """
        Read the body as yaml Content
        """
        return safe_load(self.body)

    @lazyproperty
    def title(self) -> str | None:
        """
        Get the title of the resource from the yaml body.
        """
        return self.yaml.get("title")

    @lazyproperty
    def description(self) -> str | None:
        """
        Get the description of the resource from the yaml body.
        """
        return self.yaml.get("description")

    @lazyproperty
    def tag_entry(self) -> str:
        """
        Create the text entry for the tag in the manifest.
        """

        return indent(
            dedent(
                f"""
                - tag_uri: {self.tag_uri}
                  schema_uri: {self.uri}
                  title: {self.title}
                  description: |-
                    {self.description}
                """
            ),
            " " * 2,
        )

    @property
    def is_manifest(self) -> bool:
        """
        Check if the resource is a manifest.
        """
        return "manifest" in self.uri

    def update_uri(self, current_uri: str, new_uri: str) -> _Resource:
        """
        Update all instances of the passed URI in the resource to the new one.

        Parameters
        ----------
        current_uri : str
            The current URI to update.
        new_uri : str
            The new URI to update to.

        Returns
        -------
        _Resource
            The updated resource.

        Note
        ----
        - Modifies the resource file in place on disk.
        """
        new_body = self.body.replace(current_uri, new_uri)
        with self.path.open("w") as f:
            f.write(new_body)

        return type(self).from_path(self.path, self.repository)

    def bump(self, version: str) -> _Resource:
        """
        Bump the version of the resource.
            Does this via the following steps:

            1. Rename the symlink to the new version's symlink
            2. Copy the current resource to the resources directory
            3. Update the resource's URI to the new version
        """
        # Find the new uri and path for the bumped version
        uri = self.uri.replace(self.version, version)
        path = self._find_symlink_path(self.path, version, uri)

        symlink = self.symlink
        if not symlink.exists():
            raise ValueError(f"Symlink {symlink} does not exist")
        if not symlink.is_symlink():
            raise ValueError(f"Symlink {symlink} is not a symlink")

        # 1. Rename the symlink to the new version's symlink
        self.symlink.rename(path)

        # 2. Copy the current schema to the schemas directory
        copyfile(self.path, self.symlink)

        # 3. Update the schema's URI to the new version
        return self.update_uri(self.uri, uri)

    def create(self, tagged: bool) -> _Resource:
        """
        Create the resource described by this object as part of the rad repository.
            Does this via the following steps:

            1. Modifies the body if the resource is to be tagged.
            2. Writes the body of the resource to the path
            3. Creates a symlink in the resources directory to the resource file
            4. Reads the result into a new Resource object and returns it

        Parameters
        ----------
        tagged : bool
            Whether the resource is tagged or not.

        Returns
        -------
        _Resource
            The created resource to be added to the manager.

        Effects
        -------
        - Creates the resource file at its path (in latest)
        - Creates a symlink for the resource in the resources directory
        """

        # Add the flowStyle keyword to the body if tagged
        body = self.body
        if tagged:
            body += "\nflowStyle: block\n"

        # Create the parent directory(s) if they don't exist
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

        # Create the resource file at its path (in latest)
        with self.path.open("w") as f:
            f.write(body)

        # Create the symlink parent directory(s) if they don't exist
        if not self.symlink.parent.exists():
            self.symlink.parent.mkdir(parents=True, exist_ok=True)

        # Create the symlink for the resource
        self.symlink.symlink_to(self.symlink_target)

        # Read the resource from the path and return it
        return type(self).from_path(self.path, self.repository)

    def add_tag_entry(self, entry: str) -> _Resource:
        """
        Updates a manifest resource by adding a new tag entry to the manifest.

        Parameters
        ----------
        entry : str
            The tag entry to add to the manifest.
            --> This should be a properly formatted YAML entry for a tag.

        Returns
        -------
        _Resource
            The updated resource with the new tag entry added.

        Effects
        -------
        - Modifies the manifest file in place on disk by appending the entry to the body.
        """
        if not self.is_manifest:
            raise RuntimeError("Cannot add tag entry to a non-manifest resource")

        body = self.body.rstrip() + entry
        with self.path.open("w") as f:
            f.write(body)

        return type(self).from_path(self.path, self.repository)

    def overwrite(self) -> _Resource:
        """
        Overwrite an existing resource on disk with the current body.

        Returns
        -------
        _Resource
            The resource object after overwriting the file.

        Effects
        -------
        - Writes the current body to the resource file at its path.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Resource path {self.path} does not exist")

        with self.path.open("w") as f:
            f.write(self.body)

        resource = type(self).from_path(self.path, self.repository)

        if resource.uri != self.uri:
            raise RuntimeError(f"Resource URI {resource.uri} does not match expected URI {self.uri}")

        return resource

    @staticmethod
    def _filter_ignored_keys(tree: dict[str, Any]):
        """
        Filter out the ignored keys from the dictionary.

        Parameters
        ----------
        tree :
            The tree to filter

        Returns
        -------
        The filtered tree
        """

        def filter_ignored_keys(node: Any) -> Any:
            """
            Filter out the ignored keys from the dictionary.

            Parameters
            ----------
            node : Any
                node to filter

            Returns
            -------
            dict
                The filtered dictionary
            """
            if isinstance(node, Mapping):
                return {key: value for key, value in node.items() if key not in _IGNORED_KEYWORDS}
            return node

        return walk_and_modify(tree, callback=filter_ignored_keys)

    def bump_required(self, body: str) -> bool:
        """
        Check if the body of the resource will require a bump in version if
        the passed body were to overwrite the current body.

        Parameters
        ----------
        body : str
            The body to check against the current body.

        Returns
        -------
        bool
            True if the body requires a bump, False otherwise.
        """

        return self._filter_ignored_keys(self.yaml) != self._filter_ignored_keys(safe_load(body))


class Resource(_Resource, HorizontalGroup):
    """
    A class to handle a single RAD resource inside the Textual app, by mixing the resource with a Textual widget.

    ---> Acts as a Textual Widget. It is a Horizontal item that lists the uri and asks for a new version.
             <--- uri for resource text ---><--- user interaction to enter a new version number --->

    ---> Inherits the _Resource class's functionality
    """

    class VersionValidator(Validator):
        """
        A validator to check if an entered version is valid to bump to.

        1. Checks if the version is in the format x.y.z, where x, y, and z are integers.
        2. Checks if the version is strictly greater than the current version.
           - Makes sure we aren't bumping to the same version
           - Makes sure we aren't bumping to a downgraded version.

        --> This how the input text box goes from red to blue when the user enters a valid version.

        Parameters
        ----------
        current_version : str
            The current version of the resource. (to check against)
        """

        def __init__(self, current_version: str) -> None:
            super().__init__()
            self.current_version = current_version

        def validate(self, value: str) -> ValidationResult:
            """
            Performs the validation of the input value.

            Parameters
            ----------
            value : str
                The value to validate.

            Returns
            -------
            ValidationResult
                The result of the validation, either success or failure.
            """
            pattern = r"^\d+\.\d+\.\d+$"
            if not findall(pattern, value):
                return self.failure("Invalid version format. Must be x.y.z")

            if Version(value) <= Version(self.current_version):
                return self.failure(f"Version {value} must be greater than current version")

            return self.success()

    class Bump(Message):
        """
        Message sent by the resource widget to the textual app when the user enters a valid version
        to bump the resource to.

        Parameters
        ----------
        resource : Resource
            The resource instance that is being bumped.
        bump_version : str
            The target version to bump the resource to.
        """

        def __init__(self, resource: Resource, bump_version: str) -> None:
            super().__init__()
            self.resource = resource
            self.bump_version = bump_version

    def __init__(self, uri: str, path: Path, resource: Path, body: str, frozen: bool, *args, **kwargs) -> None:
        super().__init__(uri, path, resource, body, frozen)
        super(_Resource, self).__init__(*args, **kwargs)

        self._label_width = None

    def compose(self) -> ComposeResult:
        """
        Compose (render in the App) the resource widget
        --> HorizontalGroup so its label followed by an input box
        --> the label_width is used so that all the input boxes are visually aligned, but
            this requires external knowledge so its set by the app prior to actually rendering
            the widget.
        """
        # Create the label and set its width
        label = Label(self.uri, id="uri")
        label.styles.width = self.label_width

        yield label
        # Notice that the validator is attached to the input box, its success/failure
        # will be reflected in any events triggered by the input box.
        yield Input(id="new_version", placeholder="a.b.c", validators=[self.VersionValidator(self.version)])

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Update the version of the schema when the input changes.
            -> does not use the @on decorator, because the event itself needs to
               be checked for if it is valid or not.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `input_changed`, which
              is the snake case version of the message type with periods
              replaced with underscores.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.
        --> In this Widget, there are only two children attached to the widget, by
            the compose method:
            - Label
            - Input
        --> This means that we will only get events from the Label or Input widges
            attached to this widget (no need to worry about other input boxes)

        Effects
        -------
        - Posts a Bump message event into the app if the input is valid.
          --> This will be passed upwards to the widget containing this widget
        """
        # Check that the event is from the input box labeled with "new_version"
        # --> This is a safeguard in case we decide to add more input options later
        if event.input.id == "new_version":
            # Stop the event from propagating upwards in the app
            event.stop()

            # Check if the input is valid (passes the validator)
            if event.validation_result.is_valid:
                # Create an event using the Bump message for this object
                self.post_message(self.Bump(self, event.value))

    @property
    def label_width(self) -> int:
        """
        Get the label width for the schema.
        """
        if self._label_width is None:
            # This is taken from the Textual codebase as a way to calculate the width of the
            # label based on the text length.
            text = Text.from_markup(self.uri)
            text.stylize(NULL_STYLE)
            self._label_width = text.cell_len + 10

        return self._label_width

    @label_width.setter
    def label_width(self, value: int) -> None:
        """
        Set the label width for the schema.
        """
        self._label_width = value

    def reset_width(self) -> None:
        """
        Reset the label width to None, so that it will be recalculated next time.
        """
        self._label_width = None
        # This is needed to ensure that the label width is recalculated
        # when the widget is redrawn.
        self.refresh()
