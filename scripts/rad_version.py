from __future__ import annotations

from collections.abc import Iterable, Mapping
from contextlib import suppress
from enum import StrEnum, auto
from graphlib import TopologicalSorter
from io import BytesIO
from pathlib import Path
from re import findall, sub
from shutil import copyfile
from textwrap import dedent, indent
from tomllib import load

from astropy.utils import lazyproperty
from git import Repo
from rich.style import NULL_STYLE, Style
from rich.text import Text
from semantic_version import Version
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from textual.messages import Message
from textual.screen import Screen
from textual.validation import ValidationResult, Validator
from textual.widgets import Button, DirectoryTree, Footer, Header, Input, Label, Rule, Switch
from textual.widgets._directory_tree import DirEntry
from textual.widgets._tree import TreeNode
from yaml import safe_load

REPO_DIR = Path(__file__).parent.parent
RESOURCES_DIR = REPO_DIR / "src" / "rad" / "resources"
SCHEMAS_DIR = RESOURCES_DIR / "schemas"
MANIFEST_DIR = RESOURCES_DIR / "manifests"
LATEST_DIR = REPO_DIR / "latest"
URI_PREFIX = "asdf://stsci.edu/datamodels/roman/"
SCHEMA_URI_PREFIX = f"{URI_PREFIX}schemas/"
TAG_URI_PREFIX = f"{URI_PREFIX}tags/"

RAD_URLS = (
    "https://github.com/spacetelescope/rad.git",
    "git@github.com:spacetelescope/rad.git",
)


class LatestSchema(HorizontalGroup):
    """
    A class to represent the latest RAD schema.
    """

    class VersionValidator(Validator):
        """
        A validator to check if a version is valid.
        """

        def __init__(self, current_version: str) -> None:
            super().__init__()
            self.current_version = current_version

        def validate(self, value: str) -> ValidationResult:
            pattern = r"^\d+\.\d+\.\d+$"
            if not findall(pattern, value):
                return self.failure("Invalid version format. Must be x.y.z")

            if Version(value) <= Version(self.current_version):
                return self.failure(f"Version {value} must be greater than current version")

            return self.success()

    class Bump(Message):
        def __init__(self, schema: LatestSchema, bump_version: str) -> None:
            super().__init__()
            self.schema = schema
            self.bump_version = bump_version

    def __init__(self, uri: str, path: Path, body: str, yaml: dict, frozen: bool, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.uri = uri
        self.path = path
        self.body = body
        self.yaml = yaml
        self.frozen = frozen

        self._label_width = None

    @classmethod
    def from_path(cls, path: Path, *args, **kwargs) -> LatestSchema:
        body = path.read_text()
        yaml = safe_load(body)
        uri = yaml["id"]
        return cls(uri, path, body, yaml, False, *args, **kwargs)

    @property
    def tag_uri(self) -> str:
        """
        Get the tag URI for the schema.
        """
        return sub(r"schemas", r"tags", self.uri)

    @property
    def version(self) -> str:
        """
        Get the version of the schema.
        """
        return self.uri.split("-")[-1]

    @staticmethod
    def _schema_path(path: Path, version: str, uri: str) -> str:
        """
        Get the schema symlink for the schema.
        """
        base_path = path.relative_to(LATEST_DIR)
        parent_path = base_path.parent
        filename = f"{base_path.stem}-{version}.yaml"
        if "schemas" in uri:
            return SCHEMAS_DIR / parent_path / filename
        elif "manifest" in uri:
            return MANIFEST_DIR / parent_path / filename
        else:
            raise ValueError(f"Unknown schema URI: {uri}")

    @property
    def symlink(self) -> Path:
        """
        Get the symlink for the schema.
        """
        return self._schema_path(self.path, self.version, self.uri)

    def update_uri(self, current_uri: str, new_uri: str) -> LatestSchema:
        new_body = self.body.replace(current_uri, new_uri)
        with self.path.open("w") as f:
            f.write(new_body)

        return LatestSchema.from_path(self.path)

    def bump(self, version: str) -> LatestSchema:
        """
        Bump the version of the schema.
            Does this via the following steps:

            1. Rename the symlink to the new version's symlink
            2. Copy the current schema to the schemas directory
            3. Update the schema's URI to the new version
        """
        # Find the new uri and path for the bumped version
        uri = self.uri.replace(self.version, version)
        path = self._schema_path(self.path, version, uri)

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

    def compose(self) -> ComposeResult:
        label = Label(self.uri, id="uri")
        label.styles.width = self.label_width
        yield label
        yield Input(id="new_version", placeholder="a.b.c", validators=[self.VersionValidator(self.version)])

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Update the version of the schema when the input changes.
        """
        if event.input.id == "new_version":
            event.stop()
            if event.validation_result.is_valid:
                self.post_message(self.Bump(self, event.value))

    @property
    def label_width(self) -> int:
        """
        Get the label width for the schema.
        """
        if self._label_width is None:
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


class UpdateLatestSchema(VerticalScroll):
    class Ready(Message):
        def __init__(self, versions: dict[str, str]) -> None:
            super().__init__()
            self.versions = versions

    def __init__(self, schema: LatestSchema, manager: LatestSchemaManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.schema = schema
        self.manager = manager

        self.needed_updates = self._find_needed_updates()
        self.version_updates = {}

    @classmethod
    def from_path(cls, path: Path, manager: LatestSchemaManager) -> UpdateLatestSchema:
        """
        Create an UpdateLatestSchema from a path.
        """
        return cls(manager[path], manager)

    def bump(self, versions: dict[str, str]) -> None:
        """
        Bump the versions of the schemas.
        """
        self.manager.bump(self.order, versions)

    def _find_needed_updates(self) -> dict[str, UpdateLatestSchema]:
        """
        Find the needed updates for the schema.
        """
        needed_updates = {}
        for uri, latest in self.manager.items():
            if uri == self.schema.uri:
                continue

            if self.schema.uri in latest.body or self.schema.tag_uri in latest.body:
                needed_updates[uri] = UpdateLatestSchema(latest, self.manager)

        return needed_updates

    @lazyproperty
    def graph(self) -> tuple[dict[str, set[str]], dict[str, LatestSchema]]:
        graph = {self.schema.uri: set(self.needed_updates.keys())}
        for update in self.needed_updates.values():
            graph.update(update.graph)

        return graph

    @lazyproperty
    def order(self) -> tuple[tuple[str], dict[str, LatestSchema]]:
        """
        Get the update order for the schema.
        """
        return tuple(TopologicalSorter(self.graph).static_order())

    @lazyproperty
    def frozen(self) -> tuple[LatestSchema]:
        """
        Get the frozen schemas for the update.
        """
        frozen = []
        width = 0
        for uri in self.order[::-1]:
            schema = self.manager[uri]
            if schema.frozen:
                frozen.append(schema)
                if width < schema.label_width:
                    width = schema.label_width

        for schema in frozen:
            schema.label_width = width

        return tuple(frozen)

    @lazyproperty
    def frozen_uris(self) -> set[str]:
        """
        Get the frozen schema URIs for the update.
        """
        return {schema.uri for schema in self.frozen}

    def compose(self) -> ComposeResult:
        """
        Create the child widgets for the update.
        """
        yield from self.frozen

    def on_latest_schema_bump(self, event: LatestSchema.Bump) -> None:
        event.stop()
        self.version_updates[event.schema.uri] = event.bump_version
        if self.frozen_uris == set(self.version_updates.keys()):
            self.post_message(self.Ready(self.version_updates))


class LatestSchemaManager(Mapping):
    """
    A class to manage the latest RAD schemas.
    """

    def __init__(self) -> None:
        self._latest_schemas: dict[str, LatestSchema] = {}
        self._key_map: dict[str | Path, str] = {}

        self._find_latest_schemas()

    def _find_latest_schemas(self) -> None:
        """
        Find the latest RAD schemas in the schema directory.
        """
        for path in LATEST_DIR.rglob("*.yaml"):
            self._add_schema(path)

    def _add_schema(self, path: Path) -> None:
        """
        Find a schema by its path.
        """
        schema = LatestSchema.from_path(path)
        if schema.uri in self.frozen_schema_uris:
            schema.frozen = True

        self._latest_schemas[schema.uri] = schema
        self._key_map[schema.uri] = schema.uri
        self._key_map[schema.path] = schema.uri

    @lazyproperty
    def rad_repo(self) -> Repo:
        """
        A lazy property to get the RAD repository.
        """
        return Repo(REPO_DIR)

    def update_tags(self):
        """
        Pull all the tags from the RAD Repository.
        """

        for remote in self.rad_repo.remotes:
            with suppress(AttributeError):
                url = remote.url
                if url in RAD_URLS:
                    remote.fetch(tags=True)
                    return

        raise ValueError(
            f"Unable to find the main RAD repository remote. Please add a remote with one of the following URLs: {RAD_URLS}"
        )

    @lazyproperty
    def rad_versions(self) -> tuple[str]:
        self.update_tags()

        # Find the base version from the RAD pyproject.toml file
        with (REPO_DIR / "pyproject.toml").open("rb") as f:
            base_release = Version(load(f)["tool"]["rad-versioning"]["base_release"])

        pattern = r"\d+\.\d+\.\d+$"

        versions = set()
        for tag in self.rad_repo.tags:
            if v_match := findall(pattern, tag.name):
                version = Version(v_match[-1])

                if version >= base_release:
                    versions.add(version)

        return tuple(str(v) for v in sorted(versions))

    @property
    def manifest(self) -> LatestSchema:
        """
        The manifest schema
        """
        manifests = [schema for schema in self._latest_schemas.values() if "manifest" in schema.uri]
        if len(manifests) != 1:
            raise ValueError("There should be exactly one manifest schema")

        return manifests[0]

    def _find_frozen_schema_uris(self, version: str) -> set[str]:
        """
        Find the frozen schema URIS for a given version.
        """
        release = self.rad_repo.commit(version)

        def predicate(i, d):
            """
            Determines if a file should be included in
            """
            pattern = r".*\.yaml"
            if findall(pattern, i.path):
                return True
            return False

        uris = set()
        for blob in release.tree.traverse(predicate=predicate):
            data = BytesIO(blob.data_stream.read()).read().decode("utf-8")
            if data.startswith("%YAML 1.1"):
                uris.add(safe_load(data)["id"])

        return uris

    @lazyproperty
    def frozen_schema_uris(self) -> set[str]:
        """
        A property to get the frozen schema URIs.
        """
        uris = set()
        for version in self.rad_versions:
            for uri in self._find_frozen_schema_uris(version):
                uris.add(uri)

        return uris

    @lazyproperty
    def uri_prefixes(self) -> set[str]:
        """
        A property to get the URI prefixes for the schemas.
        """
        return {uri.split("-")[0] for uri in set(self._latest_schemas.keys()) | self.frozen_schema_uris}

    def get_path(self, path: Path | str) -> str:
        """
        Find the path for a given schema.
        """
        if path not in self._key_map and isinstance(path, Path):
            self._add_schema(path)

        return self._key_map[path]

    def __getitem__(self, item: Path | str) -> LatestSchema:
        """
        Get the latest schema for a given item.
        """
        return self._latest_schemas[self.get_path(item)]

    def __setitem__(self, key: Path | str, value: LatestSchema) -> None:
        """
        Set the latest schema for a given item.
        """
        if isinstance(key, Path):
            key = value.uri

        self._latest_schemas[key] = value
        self._key_map[key] = value.uri
        self._key_map[value.path] = value.uri

    def __iter__(self):
        return iter(self._latest_schemas)

    def __len__(self) -> int:
        return len(self._latest_schemas)

    def schemas_to_bump(self, item: Path | str) -> tuple[str]:
        """
        Get the schemas that need to be bumped for a given schema.
        """
        return UpdateLatestSchema.from_schema(self[item], self).update_order

    def _update_uris(self, current_uri: str, new_uri: str) -> None:
        """
        Update the URI mentions within the schemas
        """
        for schema in self._latest_schemas.values():
            if current_uri in schema.body:
                self._latest_schemas[schema.uri] = schema.update_uri(current_uri, new_uri)

    def pop(self, item: Path | str) -> LatestSchema:
        schema = self._latest_schemas.pop(self.get_path(item))
        self._key_map.pop(schema.path)
        self._key_map.pop(schema.uri)

        return schema

    def bump(self, order: tuple[str], versions: dict[str, str]) -> None:
        for uri in order:
            if self[uri].frozen:
                current_schema = self.pop(uri)
                schema = current_schema.bump(versions[uri])
                self[schema.uri] = schema
                self._update_uris(current_schema.uri, schema.uri)
                self._update_uris(current_schema.tag_uri, schema.tag_uri)

    def update_schema(self, path: Path) -> UpdateLatestSchema:
        return UpdateLatestSchema(self[path], self)


class Rad(DirectoryTree):
    """
    A custom DirectoryTree widget to display the latest RAD schemas and their
    states.
    """

    ICON_LOCKED = "🔒"

    def __init__(self, **kwargs) -> None:
        super().__init__(LATEST_DIR, **kwargs)
        self._manager = LatestSchemaManager()

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir() or path.suffix == ".yaml"]

    def render_label(self, node: TreeNode[DirEntry], base_style: Style, style: Style) -> Text:
        """
        Modify the label of the node to indicate if it is frozen with a "🔒" symbol
        """
        base_icon = self.ICON_FILE
        if node.data.path.is_file() and node.data.path.suffix == ".yaml":
            # Check if the schema is frozen
            if safe_load(node.data.path.read_bytes())["id"] in self._manager.frozen_schema_uris:
                self.ICON_FILE = self.ICON_LOCKED
        text = super().render_label(node, base_style, style)
        self.ICON_FILE = base_icon

        return text


class ScreenReturn(StrEnum):
    """
    An enum to represent the return values for the bump screen.
    """

    BUMP = auto()
    RETURN = auto()


class BumpSchema(Screen[ScreenReturn]):
    """
    A screen to handle the bumping of a schema.
    """

    def __init__(self, update: UpdateLatestSchema, *args, button_text: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._update = update
        self._versions = None
        self._button_text = "Bump Schema" if button_text is None else button_text

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalGroup(id="controls"):
            with HorizontalGroup(id="buttons"):
                yield Button(self._button_text, id="bump_schemas", variant="success", disabled=True)
                yield Button("Return", id="return", variant="error")
            yield Rule()
            yield Label("Please fill in the new version number for each schema listed below:")
            yield Rule()
            yield self._update
        yield Footer()

    @on(Button.Pressed, "#return")
    def handle_return(self) -> None:
        """
        Handle the return button press.
        """
        self.dismiss(ScreenReturn.RETURN)

    @on(Button.Pressed, "#bump_schemas")
    def handle_bump(self) -> None:
        """
        Handle the bump button press.
        """
        self._update.bump(self._versions)
        self.dismiss(ScreenReturn.BUMP)

    def on_update_latest_schema_ready(self, event: UpdateLatestSchema.Ready) -> None:
        self.query_one("#bump_schemas", Button).disabled = False
        self._versions = event.versions


class NewSchema(Screen[ScreenReturn]):
    """
    A screen to handle the creation of a new schema.
    """

    _URI_LABEL = f"New URI: {SCHEMA_URI_PREFIX}"

    class SuffixValidator(Validator):
        """
        A validator to check if a version is valid.
        """

        def __init__(self, manager: LatestSchemaManager) -> None:
            super().__init__()
            self.manager = manager

        def validate(self, value: str) -> ValidationResult:
            # Check the end of the suffix is a valid version URI
            pattern = r"^.*-\d+\.\d+\.\d+$"
            if not findall(pattern, value):
                return self.failure("Invalid version format. Must be x.y.z")

            # Check that the suffix has only one `-` in it
            if value.count("-") != 1:
                return self.failure("Invalid version format. Must be x.y.z")

            # Check that the suffix is not already in use
            if f"{SCHEMA_URI_PREFIX}{value.split('-')[0]}" in self.manager.uri_prefixes:
                return self.failure(f"Schema {SCHEMA_URI_PREFIX}{value} already exists.")

            return self.success()

    def __init__(self, manager: LatestSchemaManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._manager = manager

    @lazyproperty
    def label_width(self) -> int:
        """
        Get the label width for the schema.
        """
        text = Text.from_markup(self._URI_LABEL)
        text.stylize(NULL_STYLE)
        return text.cell_len + 5

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalGroup(id="controls"):
            with HorizontalGroup(id="buttons"):
                yield Button("Create New Schema", id="create_schema", variant="success", disabled=True)
                yield Button("Return", id="return", variant="error")
            yield Rule()
            yield Label("Please fill in the new schema details:")
            yield Rule()
            with HorizontalGroup(id="uri_input"):
                uri_label = Label(self._URI_LABEL, id="uri_label")
                uri_label.styles.width = self.label_width
                yield uri_label
                yield Input(id="new_uri", placeholder="new_schema-a.b.c", validators=[self.SuffixValidator(self._manager)])
            with HorizontalGroup(id="title_input"):
                title_label = Label("Title:", id="title_label")
                title_label.styles.width = self.label_width
                yield title_label
                yield Input(id="new_title", placeholder="Title of the new schema")
            with HorizontalGroup(id="tagged_input"):
                tag_label = Label("Tagged:", id="tagged_label")
                tag_label.styles.width = self.label_width
                yield tag_label
                yield Switch(value=False, id="tag", disabled=True)
            with HorizontalGroup(id="description_input"):
                description_label = Label("Description:", id="description_label")
                description_label.styles.width = self.label_width
                yield description_label
                yield Input(id="new_description", placeholder="Description of the new schema", disabled=True)
        yield Footer()

    @on(Button.Pressed, "#return")
    def handle_return(self) -> None:
        self.dismiss(ScreenReturn.RETURN)

    def _set_create_state_disabled(self) -> None:
        uri_valid = self.query_one("#new_uri", Input).is_valid

        uri_text = self.query_one("#new_uri", Input).value
        title_text = self.query_one("#new_title", Input).value
        description_text = self.query_one("#new_description", Input).value

        tag_state = self.query_one("#tag", Switch).value

        if uri_valid and (
            (tag_state and uri_text and title_text and description_text) or (not tag_state and uri_text and title_text)
        ):
            self.query_one("#tag", Switch).disabled = False
            self.query_one("#create_schema", Button).disabled = False
        else:
            self.query_one("#tag", Switch).disabled = True
            self.query_one("#create_schema", Button).disabled = True

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Update the version of the schema when the input changes.
        """
        if event.input.id in ("new_uri", "new_title", "new_description"):
            event.stop()
            self._set_create_state_disabled()

    @on(Switch.Changed, "#tag")
    def handle_tag(self) -> None:
        if self.query_one("#tag", Switch).value:
            self.query_one("#new_description", Input).disabled = False
            self._set_create_state_disabled()
        else:
            self.query_one("#new_description", Input).disabled = True
            self.query_one("#new_description", Input).value = None
            self._set_create_state_disabled()

    @work
    @on(Button.Pressed, "#create_schema")
    async def handle_create_schema(self) -> None:
        """
        Handle the creation of a new schema.
        """
        if self.query_one("#tag", Switch).value:
            manifest = self._manager.manifest
            if manifest.frozen:
                match await self.app.push_screen_wait(
                    BumpSchema(
                        UpdateLatestSchema.from_path(manifest.path, self._manager), button_text="Bump Manifest and Create Schema"
                    )
                ):
                    case ScreenReturn.BUMP:
                        self.notify("Manifest bumped successfully.", severity="success")
                    case ScreenReturn.RETURN:
                        self.notify("Returned to new schema without bumping manifest.", severity="info")
                        return
                    case _:
                        self.notify("Something went wrong while bumping the manifest.", severity="error")
                        return

        self._create_new_schema()
        self.dismiss(ScreenReturn.BUMP)

    def _create_new_schema(self) -> None:
        """
        Create a new schema
        """
        uri_suffix = self.query_one("#new_uri", Input).value
        uri = f"{SCHEMA_URI_PREFIX}{uri_suffix}"
        file_path = LATEST_DIR / f"{uri_suffix.split('-')[0]}.yaml"
        if file_path.exists():
            self.notify(f"File {file_path} already exists.", severity="error")
            return
        symlink_path = SCHEMAS_DIR / f"{uri_suffix}.yaml"
        if symlink_path.exists():
            self.notify(f"Symlink {symlink_path} already exists.", severity="error")
            return
        target_path = file_path.relative_to(symlink_path.parent, walk_up=True)

        title = self.query_one("#new_title", Input).value
        schema_text = dedent(
            f"""
            %YAML 1.1
            ---
            $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
            id: {uri}

            title: {title}
            """
        ).lstrip()

        if self.query_one("#tag", Switch).value:
            schema_text += "\nflowStyle: block\n"

            # Remove the ... at the end
            manifest = self._manager.manifest

            tag_uri = f"{TAG_URI_PREFIX}{uri_suffix}"
            description = indent(self.query_one("#new_description", Input).value, "  ")

            entry = dedent(
                f"""
                - tag_uri: {tag_uri}
                  schema_uri: {uri}
                  title: {title}
                  description: |-
                  {description}
                """
            )
            body = manifest.body.rstrip().rsplit("\n", 1)[0]
            manifest.body = f"{body}\n{entry}\n...\n"
            with manifest.path.open("w") as f:
                f.write(manifest.body)

        schema_text += "...\n"
        with file_path.open("w") as f:
            f.write(schema_text)
        if not file_path.exists():
            raise ValueError(f"Failed to create file {file_path}")

        symlink_path.symlink_to(target_path)
        if not symlink_path.exists() and not symlink_path.is_symlink():
            raise ValueError(f"Failed to create symlink {symlink_path}")

        if symlink_path.resolve() != file_path:
            raise ValueError(f"Symlink {symlink_path} does not point to {file_path}")

        self._manager[uri] = LatestSchema.from_path(file_path)
        self.dismiss(ScreenReturn.BUMP)


class RadVersioningApp(App):
    """A Textual app to manage RAD schemas."""

    CSS_PATH = "update_view.tcss"

    BINDINGS = (
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._manager = LatestSchemaManager()
        self._rad = Rad(id="rad")
        self._update_path = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalGroup(id="controls"):
            with HorizontalGroup(id="buttons"):
                yield Button("Create New Schema", id="create_new_schema", variant="success")
                yield Button("Bump", id="bump", variant="primary", disabled=True)
                yield Button("Quit", id="quit", variant="error")
            yield Rule()
            yield Label("Select a schema to bump or select 'Create New Schema':")
            yield Rule()
            yield self._rad
        yield Footer()

    @work
    @on(Button.Pressed, "#create_new_schema")
    async def handle_create_new_schema(self) -> None:
        """
        Handle the create schema button press.
        """
        match await self.push_screen_wait(NewSchema(self._manager)):
            case ScreenReturn.BUMP:
                self._rad.reload()
                self.notify("New schema created successfully.", severity="success")
            case ScreenReturn.RETURN:
                self._rad.reload()
                self.notify("Returned to main menu without creating a new schema.", severity="info")
            case _:
                self.notify("Something went wrong while creating the new schema.", severity="error")

    @on(Button.Pressed, "#quit")
    def handle_quit(self) -> None:
        self.exit()

    @work
    @on(Button.Pressed, "#bump")
    async def handle_bump(self) -> None:
        """
        Handle the bump button press.
        """
        match await self.push_screen_wait(BumpSchema(UpdateLatestSchema.from_path(self._update_path, self._manager))):
            case ScreenReturn.BUMP:
                self._rad.reload()
                self.notify("Schemas bumped successfully.", severity="success")
            case ScreenReturn.RETURN:
                self._rad.reload()
                self.notify("Returned to main menu without bumping.", severity="info")
            case _:
                self.notify("Something went wrong while bumping the schema.", severity="error")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """
        Handle the selection of a file in the directory tree.
        """
        if event.path.is_file() and event.path.suffix == ".yaml" and self._manager[event.path].frozen:
            self._update_path = event.path
            self.query_one("#bump", Button).disabled = False
        else:
            self.query_one("#bump", Button).disabled = True


if __name__ == "__main__":
    app = RadVersioningApp()
    app.run()
