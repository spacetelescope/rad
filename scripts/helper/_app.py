"""
This module provides the actual Textual application object that drives the CLI GUI.
"""

from __future__ import annotations

from os import environ
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Rule, TabbedContent

from ._edit import EditTab
from ._manager import Manager
from ._resource import Resource
from ._screen import BumpScreen, NewScreen

__all__ = ("RadApp",)


class RadApp(App):
    """
    The CLI GUI application for assisting with RAD development.

    ---> Main screen layout

        <--- Header (RAD Development Assistant) --->
        <--- Tabbed Content --->
        | Bump Tab (default) |
             <--- BumpTab widget --->
        | New Resource Tab     |
            <--- nothing yet --->
        <--- Rule (heavy line) --->
        <--- Button (Quit) --->
        <--- Rule --->
        <--- Footer (global controls and options) --->

    ---> Global bindings (outside of text input fields)
        q: Quit the application
        d: Toggle dark mode
        e: Show the edit tab

    Parameters
    ----------
    path : Path
        The path to the RAD project directory. (To be passed in by the CLI script itself)
    """

    CSS_PATH = "rad_app.tcss"

    # Global bindings for the app
    BINDINGS = (
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("e", "show_tab('edit')", "Edit Resources"),
    )

    def __init__(self, path: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._manager = Manager(path)

    def compose(self) -> ComposeResult:
        """
        Compose (render in the App) the App's Main screen layout.
        """
        yield Header("RAD Development Assistant")

        # Add the TabbedContent widget
        with TabbedContent(initial="edit"):
            yield EditTab(self._manager, id="edit")

        yield Rule(line_style="heavy")
        yield Button("Quit", id="quit", variant="error")
        yield Rule()
        yield Footer()

    def action_show_tab(self, tab: str) -> None:
        """
        Switch to a new tab

        --> Textual wires stuff together based on names:
           - `action_` in this case means some action that will update the UI.
             is performed by the method.
           - Next path is the name of the action. So `show_tab` is the action name.
             See the `BINDINGS` for the keybinding that triggers this action.
        """
        self.get_child_by_type(TabbedContent).active = tab

    @on(Button.Pressed, "#quit")
    def handle_quit(self) -> None:
        """
        Handle the quit button press.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "quit".

        Effect
        ------
        Exits the application gracefully.
        """
        self.exit()

    @work
    async def on_edit_tab_bump_screen(self, event: EditTab.BumpScreen) -> None:
        """
        Handle the BumpScreen message to show the bump screen and then wait for
        the result.
            -> does not use the @on decorator, because the event message is needed
               to extract the bump generator.
            -> @work decorator is used so that Textual can run this method in a
               separate thread to await the result without having to re-render the
               rest of the UI.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `bump_tab_bump_screen`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `EditTab.BumpScreen` object
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.
        ---> this will only be triggered by the single EditTab widget.

        Effects
        -------
        - Displays the BumpScreen to the user.
        - Waits for the user's response to the bump screen.
        - Executes the user's choice from the bump screen and pushes a notification
          to the screen informing them of the result.
        """
        await self._bump_resources(event.screen)

    async def _bump_resources(self, screen: BumpScreen):
        """
        Reusable method to display and handle the output of a BumpScreen.

        Parameters
        ----------
        screen : BumpScreen
            The bump screen to display to the user.

        Returns
        -------
        BumpScreen.Return
            The result of the bump operation, which can be either Bump or Return.

        Effects
        -------
        - Displays the BumpScreen to the user.
        - Waits for the user's response to the bump screen.
        - Executes the user's choice from the bump screen including making changes
          to the resources if required.
        """
        # Launch the bump screen and wait for the result
        state, generator = await self.push_screen_wait(screen)

        # Execute the selected action from the bump screen
        self._manager.bump(state, generator)

        return state

    @work
    async def on_edit_tab_new_screen(self, event: EditTab.NewScreen) -> None:
        """
        Handle the NewScreen message to show the new screen and then wait for
        the result.
            -> does not use the @on decorator, because the event message is needed
               to extract the new resource.
            -> @work decorator is used so that Textual can run this method in a
               separate thread to await the result without having to re-render the
               rest of the UI.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `bump_tab_new_screen`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `EditTab.BumpScreen` object
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.
        ---> this will only be triggered by the single EditTab widget.

        Effects
        -------
        - Displays the NewScreen to the user.
        - Waits for the user's response to the new screen.
        - If a bump is required, it will display, wait for and handle the result
          of a BumpScreen.
        - Executes the user's choice from the new screen and pushes a notification
          to the screen informing them of the result.
        """
        # Launch the bump screen and wait for the result
        state, tagged, new_resource = await self.push_screen_wait(event.screen)

        if state == NewScreen.Return.RETURN:
            self.notify("No new resource was created.", severity="info")
            return

        if tagged:
            if self._manager.datamodels_manifest.frozen:
                match await self._bump_resources(BumpScreen(self._manager.init_bump(self._manager.datamodels_manifest.path))):
                    case BumpScreen.Return.BUMP:
                        self.notify("Resources bumped successfully.", severity="success")
                    case BumpScreen.Return.RETURN:
                        self.notify("Could not bump the manifest, aborting resource creation", severity="error")
                        return
            self._manager.add_tag_entry(new_resource.tag_entry)

        self._manager.add_new_resource(state, new_resource.create(tagged))

    def _run_editor(self, path: Path) -> None:
        """
        Run the editor for the given path.

        Parameters
        ----------
        path : Path
            The path to the file to edit.

        Effects
        -------
        - Suspends the application.
        - Runs the $EDITOR (or vim by default) on the given path
        - Resumes the application after the editor is closed.
        """
        with self.suspend():
            run(  # noqa: S603
                [environ.get("EDITOR", "vim"), str(path)],
                check=True,
            )

    @work
    async def on_edit_tab_start_edit(self, event: EditTab.StartEdit) -> None:
        """
        Handle the EditTab.StartEdit message, which kicks off an editing session
        for a given resource.
            -> does not use the @on decorator, because the event message is needed
               to extract the new resource.
            -> @work decorator is used so that Textual can run this method in a
               separate thread to await the result without having to re-render the
               rest of the UI.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `edit_tab_start_edit`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `EditTab.StartEdit` object
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.

        ---> this will only be triggered by the single EditTab widget.
        Handle the StartEdit message to open the editor for the selected resource.

        Parameters
        ----------
        event : EditTab.StartEdit
            The event containing the path to the resource to edit.

        Effects
        -------
        - Copies the contents of the resource to a temporary file.
        - Opens the editor on the temporary file.
        - If the resource was frozen and the body has changed in a way that
          requires a bump, it will display a BumpScreen to the user.
        - If the user bails on the bump, it will save the modified body to an
          alternate file in the unsaved path.
        - If the user completes the bump, the necessary bump operations will be
          performed
        - The body changes will be applied to the resource file itself.
        - A notification will be pushed to the screen informing the user of the
          result of the operation.
        """
        # Create a temporary file so that the actual file is modified if
        # a bailout occurs
        with TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / event.resource.path.name

            # Write the current contents of the resource to the temporary file
            with tmp_file.open("w") as f:
                f.write(event.resource.body)

            # Open the editor on the temporary file
            self._run_editor(tmp_file)

            with tmp_file.open("r") as f:
                new_body = f.read()

            # Bump the resource if it is frozen and the body has changed
            if event.resource.frozen and event.resource.bump_required(new_body):
                match await self._bump_resources(BumpScreen(self._manager.init_bump(event.resource.path))):
                    case BumpScreen.Return.BUMP:
                        self.notify("Resources bumped successfully.", severity="success")

                        # Since a bump occurred, we need to update the resource body
                        # to reflect any URI changes that may have occurred.
                        # --> In most cases, this will only be the main resource id field.
                        # --> If the resource is a manifest, then the extension_uri will also change
                        #     this is actually just the tag_uri of the resource.
                        resource = self._manager[event.resource.path]
                        new_body = new_body.replace(event.resource.uri, resource.uri)
                        new_body = new_body.replace(event.resource.tag_uri, resource.tag_uri)

                    # Bailout if the bump fails
                    case BumpScreen.Return.RETURN:
                        self.notify(
                            "Could not bump resources, aborting resource modification. Saving to alternate file", severity="error"
                        )
                        with (self._manager.unsaved_path / event.resource.path.name).open("w") as f:
                            f.write(new_body)
                        return

            self._manager.edit_resource(Resource.from_body(new_body, event.resource.repository))
