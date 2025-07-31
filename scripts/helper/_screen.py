"""
This module defines two custom Textual Screens, which will be overlaid on the main
application to allow the user to input specific information:

- `BumpScreen`: For performing a bump operation on resources.
- `NewScreen`: For creating a new resource with user-defined properties.
"""

from __future__ import annotations

from collections.abc import Generator
from enum import StrEnum, auto
from typing import TYPE_CHECKING, TypeVar

from rich.style import NULL_STYLE
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.screen import Screen
from textual.validation import ValidationResult
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet, Rule, Switch

from ._bump import Bump
from ._resource import Resource

if TYPE_CHECKING:
    from ._manager import Manager

__all__ = ("BumpScreen", "NewScreen")


_T = TypeVar("_T")


class _Screen(Screen[_T]):
    """
    A base class for the screens so the return values can be reused in both
    """

    class Return(StrEnum):
        """
        An enum to represent the return values for the bump screen.
        ---> In case we need to add more return options in the future.
        """

        BUMP = auto()
        RETURN = auto()
        CREATE = auto()
        EDIT = auto()


class BumpScreen(_Screen[tuple[_Screen.Return, Generator[Resource | None, None, None]]]):
    """
    Custom Textual Screen that overlays the main app to allow the user to interact
    with a resource to enter the necessary information to accomplish the bump operation.

    --> This is a Textual Screen, which will be launched and awaited by the App
        and is expected to dismiss with a tuple

        (Return.<type>, Generator[Resource | None, None, None])

    --> Screens do not post messages, but instead are dismissed with some data
        that is returned to the place where the screen was launched.

    --> The layout will use the default Header and Footer from the App so the
        global controls are still available to the user.

        <---Header (Bump)--->
        <---Button (<bump_text>)---> <---Button (Return)--->
        <---Rule--->
        <---Label (<instruction text>)--->
        <---Rule--->
        <---Bump Widget --->
        <---Footer (default)--->

    Parameters
    ----------
    update : Bump
        The Bump instance that contains the resources to be bumped and the generator
        for the bump updates.
    button_text : str | None, optional
        The text for the bump button, by default "Bump Resource(s)"
    """

    def __init__(self, bump: Bump, *args, button_text: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._bump = bump
        self._bump_generator: Generator[Resource, None, None] | None = None
        self._button_text = "Bump Resource(s)" if button_text is None else button_text

    def compose(self) -> ComposeResult:
        """
        Compose (render in the App) the bump screen
        ---> See the main docstring for the layout
        """
        yield Header("Bump")
        with VerticalGroup(id="controls"):
            with HorizontalGroup(id="buttons"):
                # The bump_resources button is disabled until the Bump widget is ready
                # ---> It will not be clickable until the user has entered valid version numbers
                #      for all resources in the Bump widget
                yield Button(self._button_text, id="bump_resources", variant="success", disabled=True)
                yield Button("Return", id="return", variant="error")
            yield Rule()
            yield Label("Please fill in the new version number for each resource listed below:")
            yield Rule()
            yield self._bump
        yield Footer()

    @on(Button.Pressed, "#return")
    def handle_return(self) -> None:
        """
        Handle the return button press.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "return".

        Effects
        -------
        - Dismiss the screen with message indicating no bump was performed.
        - Include a tuple so that the app can then reset the resources
        """
        self.dismiss((self.Return.RETURN, self._bump.reset()))

    @on(Button.Pressed, "#bump_resources")
    def handle_bump(self) -> None:
        """
        Handle the bump button press.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "bump_resources".

        Effects
        -------
        - Dismiss the screen with a tuple containing the Return.BUMP and the bump generator.
        - The generator will then be used by the app to apply the updates to the resources.
        """
        # Sanity check to ensure nothing has gone seriously wrong in the App
        if self._bump_generator is None:
            raise RuntimeError("Something went wrong with the bump screen, bump enabled but no bump generator found.")

        self.dismiss((self.Return.BUMP, self._bump_generator))

    def on_bump_ready(self, event: Bump.Ready) -> None:
        """
        Update the screen when the Bump widget is ready to perform the bump operation.
        and store the bump generator for if/when the user needs it.
            -> does not use the @on decorator, because the event message is needed
               to extract the bump generator.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `bump_ready`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `Bump.Ready` object.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.
        ---> this will only be triggered by the single Bump widget in this screen

        Effects
        -------
        - Enable the bump button and store the bump generator for later use.
        """
        self.query_one("#bump_resources", Button).disabled = False
        self._bump_generator = event.bump


class NewScreen(_Screen[tuple[_Screen.Return, bool | None, Resource | None]]):
    """
    Custom Textual Screen to handle the entry of the information to create a new resource.

    --> This is a Textual Screen, which will be launched and awaited by the App
        and is expected to dismiss with a

        BumpScreen.Return.<type>

    --> Screens do not post messages, but instead are dismissed with some data
        that is returned to the place where the screen was launched.

    --> The layout will use the default Header and Footer from the App so the
        global controls are still available to the user.

        <---Header (Create New Resource)--->
        <---Button (Create)---> <---Button (Return)--->
        <---Rule--->
        <---Label (<instruction text>)--->
        <---Rule--->
        <---Label (Title:)---> <---Input (new_title)--->
        <---Label (Description:)---> <---Input (new_description)--->
        <---Rule--->
        <---RadioSet (uri_prefix selection) ---><---Input (uri_suffix)--->
            <---RadioButton (schema_prefix)  --->
            <---RadioButton (manifest_prefix)--->
        <---Rule--->
        <---Label (Tagged:)---> <---Switch (tagged toggle)--->
        <---Footer (default)--->

    --> The Control Scheme is a bit complicated as there are multiple inputs and
        requirements:

        1. Title is always required.
        2. Description is required if a resource is tagged or is a manifest.
        3. The URI prefix must be selected before with options for:
            -> schema
            -> manifest
        4. The URI suffix must be filled in and valid:
           -> Blocked until the URI prefix is selected.
        5. The manifests cannot be tagged, so the tagged switch is disabled

        Once a requirement combination is met, the Create button is enabled
        --> If a change is made that invalidates the requirements, the Create
            button is disabled again.

    Parameters
    ----------
    manager : Manager
        The manager instance to check against existing schemas and manifests.
    """

    class SuffixValidator(Resource.VersionValidator):
        """
        A validator to check if a uri_suffix is valid:

        1. It must not be empty.
        2. It must contain exactly one `-` character, which separates the base name from the version suffix.
        3. The base name (before the `-`) must not already exist as a schema or manifest resource in the manager.
        4. The version suffix (after the `-`) must be a valid version string, see `Resource.VersionValidator`.

        Parameters
        ----------
        manager : Manager
            The manager instance to check against existing schemas and manifests.
        """

        def __init__(self, manager: Manager) -> None:
            super().__init__("0.0.0")
            self.manager = manager

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
            if not value:
                return self.failure("URI suffix cannot be empty.")

            # Check that the suffix has only one `-` in it
            if value.count("-") != 1:
                return self.failure("Invalid suffix format. Must end with a version suffix like `-a.b.c`")

            # Check that the suffix is not already in use as a schema
            if f"{Resource.SCHEMA_URI_PREFIX}{value.split('-')[0]}" in self.manager.prefixes:
                return self.failure(f"Schema {Resource.SCHEMA_URI_PREFIX}{value} already exists.")

            # Check that the suffix is not already in use as a manifest
            if f"{Resource.MANIFEST_URI_PREFIX}{value.split('-')[0]}" in self.manager.prefixes:
                return self.failure(f"Manifest {Resource.MANIFEST_URI_PREFIX}{value} already exists.")

            return super().validate(value.split("-")[-1])

    def __init__(self, manager: Manager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._manager = manager

    def compose(self) -> ComposeResult:
        """
        Compose (render in the App) the bump screen
        ---> See the main docstring for the layout
        """
        yield Header("Create New Resource")

        # Buttons and directions
        with VerticalGroup(id="controls"):
            with HorizontalGroup(id="buttons"):
                yield Button("Create", id="create", variant="success", disabled=True)
                yield Button("Return", id="return", variant="error")
            yield Rule()
            yield Label("Please fill in the new resource details:")
            yield Rule()

            # Title and description inputs
            text = Text.from_markup("Description:")
            text.stylize(NULL_STYLE)
            width = text.cell_len + 5
            with HorizontalGroup(id="title_input"):
                title = Label("Title:", id="title_label")
                title.styles.width = width
                yield title
                yield Input(id="new_title", placeholder="Title of the new resource")
            with HorizontalGroup(id="description_input"):
                description_label = Label("Description:", id="description_label")
                description_label.styles.width = width
                yield description_label
                yield Input(id="new_description", placeholder="Description of the new resource")
            yield Rule()

            # URI construction inputs
            with HorizontalGroup(id="uri_input"):
                with RadioSet(id="uri_prefix"):
                    yield RadioButton(f"Schema uri  : {Resource.SCHEMA_URI_PREFIX}", id="schema_prefix")
                    yield RadioButton(f"Manifest uri: {Resource.MANIFEST_URI_PREFIX}", id="manifest_prefix")

                uri_input = Input(
                    id="uri_suffix",
                    placeholder="new_schema-a.b.c",
                    validators=[self.SuffixValidator(self._manager)],
                    disabled=True,
                )
                uri_input.styles.height = "100%"
                uri_input.styles.width = "80%"
                yield uri_input
            yield Rule()

            # Turn on/off tagging of the resource
            with HorizontalGroup(id="tagged_input"):
                yield Label("Tagged:", id="tagged_label")
                yield Switch(value=False, id="tagged", disabled=True)
        yield Footer()

    @property
    def new_title(self) -> str:
        """
        Get the title of the new resource from the input field.
        """
        return self.query_one("#new_title", Input).value.strip()

    @property
    def new_description(self) -> str:
        """
        Get the description of the new resource from the input field.
        """
        return self.query_one("#new_description", Input).value.strip()

    @property
    def tagged(self) -> bool:
        """
        Get the tagged state from the switch.
        """
        return self.query_one("#tagged", Switch).value

    @property
    def uri_prefix(self) -> str | None:
        """
        Get the URI prefix from the radio set.
        """
        button = self.query_one("#uri_prefix", RadioSet).pressed_button
        return button.id if button else None

    @property
    def uri_suffix(self) -> str:
        """
        Get the URI suffix from the input field.
        """
        uri_suffix = self.query_one("#uri_suffix", Input)
        if uri_suffix.is_valid and self.uri_prefix in ("schema_prefix", "manifest_prefix"):
            return uri_suffix.value.strip()

        return None

    @property
    def resource(self) -> Resource | None:
        """
        Get the resource object based on the URI prefix and suffix.
        """
        if (uri_suffix := self.uri_suffix) is not None:
            match self.uri_prefix:
                case "schema_prefix":
                    return Resource.schema_from_uri_suffix(
                        uri_suffix, self._manager.repository, self.new_title, self.new_description
                    )
                case "manifest_prefix":
                    return Resource.manifest_from_uri_suffix(
                        uri_suffix, self._manager.repository, self.new_title, self.new_description
                    )

        return None

    @on(Button.Pressed, "#return")
    def handle_return(self) -> None:
        """
        Handle the return button press.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "return".

        Effects
        -------
        - Dismiss the screen with message indicating no new resource was created.
        """
        self.dismiss((self.Return.RETURN, None, None))

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """
        Update the screen's enable/disable for input controls based on the selected URI prefix.
            -> does not use the @on decorator, because the event message is needed
               to extract the the state

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `radio_set_changed`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `RadioSet.Changed` object.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.
        ---> this will only be triggered by the single RadioSet in this screen

        Effects
        -------
        - Update the status of all the controls based on the logic defined in the
          class's docstring.
        """
        # A selection has been made, so enable the URI suffix input
        self.query_one("#uri_suffix", Input).disabled = False

        self._set_tagged_state()
        self._set_create_state()

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Update the screen's enable/disable for input controls based on the inputs
        to text input fields
            -> does not use the @on decorator, because the event message is needed
               to extract the the state

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `input_changed`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `Input.Changed` object.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.

        Effects
        -------
        - Update the status of all the controls based on the logic defined in the
          class's docstring.
        """
        self._set_tagged_state()
        self._set_create_state()

    def _set_tagged_state(self) -> None:
        """
        Update the tagged switch enable/disable state based on the URI prefix.
        --> See the class's docstring for the logic.
        """
        # Depends on the prefix selected
        match self.uri_prefix:
            case "schema_prefix":
                # If no suffix is provided, disable the tagged switch
                # but enable it if a suffix is provided
                if self.uri_suffix is None:
                    self.query_one("#tagged", Switch).disabled = True
                else:
                    self.query_one("#tagged", Switch).disabled = False

            case "manifest_prefix":
                # Disable the tagged switch for manifest URIs
                self.query_one("#tagged", Switch).disabled = True
                self.query_one("#tagged", Switch).value = False

    def _set_create_state(self) -> None:
        """
        Update the create button enable/disable state based on the inputs.
        --> See the class's docstring for the logic.

        """
        # Create requires a new_title and a resource (i.e. not None) to be created
        # Additionally it requires one of the following:
        # - If tagged, a new_description must be provided
        # - If not tagged, no new_description is required (but can be provided)
        if self.new_title and self.resource and ((self.tagged and self.new_description) or not self.tagged):
            # Enable the create button if all required fields are filled in
            self.query_one("#create", Button).disabled = False
        else:
            self.query_one("#create", Button).disabled = True

    @on(Switch.Changed, "#tagged")
    def handle_tag(self) -> None:
        """
        Handle the tagged switch input.
        ---> `@on` decorator says that this method will be called when a Switch.Changed event is
             triggered on a switch with the id "tagged".

        Effects
        -------
        - Update the create button's state
        """
        self._set_create_state()

    @on(Button.Pressed, "#create")
    def handle_create(self) -> None:
        """
        Handle the create button press.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "create".

        Effects
        -------
        - Dismiss the screen with a tuple containing
            (Return.CREATE, tagged state, resource object)
        """
        self.dismiss((self.Return.CREATE, self.query_one("#tagged", Switch).value, self.resource))
