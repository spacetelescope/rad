"""
This module defines a custom Textual widget for creating, editing, and bumping RAD resources.
--> This is where all the main functionality ties together.
"""

from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.messages import Message
from textual.widgets import Button, DirectoryTree, Label, Rule, TabPane

from ._manager import Manager
from ._resource import Resource
from ._screen import BumpScreen, NewScreen

__all__ = ("EditTab",)


class EditTab(TabPane):
    """
    Custom Textual TabPane widget for the main app that allows the user to edit resources:
        - Create a new resource
        - Edit an existing resource
        - Bump a frozen resource

    --> Layout within the TabPane:
        <---Button (New)---><---Button (Edit)---><---Button (Bump)--->
        <---Rule--->
        <---Label (instruction text)---><---Label (<updates to selected resource>)--->
        <---Rule--->
        <---Manager (DirectoryTree, for resource selection) widget--->

    --> The control enable scheme is as follows:
        1. New button is always enabled.
        2. Edit button is enabled only when a resource is selected.
        3. Bump button is enabled only when a frozen resource is selected.
           (i.e. the resource is locked and needs to be bumped to be unlocked)

    Parameters
    ----------
    manager : Manager
        The Manager instance that is used to manage the resources.
        This is used to initialize the DirectoryTree and other widgets.
    """

    class BumpScreen(Message):
        """
        A message to the main App to display a BumpScreen.
        --> Only the core app can display a screen, so this message is used
            to communicate that to the main app

        Parameters
        ----------
        path : Path
            The path to the resource that is to be bumped.
            This is used to initialize the BumpScreen with the correct resource.
        manager : Manager
            The Manager instance that is used to initialize the BumpScreen.

        Attributes
        ---------
        screen : BumpScreen
            The BumpScreen instance to be displayed.
            This is the screen that will allow the user to enter the new version numbers
            for the resources to be bumped.
        """

        def __init__(self, path: Path, manager: Manager) -> None:
            super().__init__()
            self.screen = BumpScreen(manager.init_bump(path))

    class NewScreen(Message):
        """
        A message to the main App to display a NewScreen.
        --> Only the core app can display a screen, so this message is used
             to communicate that to the main app

        Parameters
        ----------
        manager : Manager
            The Manager instance that is used to initialize the NewScreen.

        Attributes
        ---------
        screen : NewScreen
            The NewScreen instance to be displayed.
            This is the screen that will allow the user to enter the details for
            a new resource for the resources to be bumped.
        """

        def __init__(self, manager: Manager) -> None:
            super().__init__()
            self.screen = NewScreen(manager)

    class StartEdit(Message):
        """
        A message to the main App to edit a resource.
        --> Only the core app can suspend itself and allow another terminal process
            to run

        Parameters
        ----------
        resource : Resource
            The resource that is to be edited.
            This is used to start a terminal process to edit the resource.
        """

        def __init__(self, resource: Resource) -> None:
            super().__init__()
            self.resource = resource

    def __init__(self, manager: Manager, *args, **kwargs) -> None:
        super().__init__("Edit Resources", *args, **kwargs)
        self._manager = manager
        self._selection: Path | None = None

    def compose(self) -> ComposeResult:
        """
        Compose (render in the App) the ResourceTab Widget.
        --> See the class docstring for the layout of the widget.
        """
        with HorizontalGroup(id="resource_controls"):
            yield Button("New", id="new_resource", variant="success")
            yield Button("Edit", id="edit_resource", variant="primary", disabled=True)
            yield Button("Bump", id="bump_resource", variant="warning", disabled=True)

        yield Rule()
        with HorizontalGroup(id="directions"):
            directions = Label(f"Select a resource to edit or bump a locked resource (marked with {Manager.ICON_LOCKED}):")
            directions.styles.border = ("solid", "blue")
            yield directions
            selection = Label("", id="selection")
            selection.styles.border = ("solid", "green")
            yield selection
        yield Rule()

        yield self._manager

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """
        Handle the selection of a file in the directory tree.
            -> does not use the @on decorator, because the event itself needs to
               be queried for the path to the selected file.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `directory_tree_file_selected`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `textual.widget.DirectoryTree.FileSelected` object.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.

        Effects
        -------
        - If the file selected is a yaml file (so a resource):
            - Store the path to the selected file in `_selection`.
            - Enable the edit_resource button.
            - If the file is frozen, then enable the bump_resource button,
              otherwise disable the bump_resource button.
        - Otherwise (the file is something else, this is a safeguard):
            - Set `_selection` to None.
            - Disable the edit_resource button.
            - Disable the bump_resource button.
        """
        if event.path.suffix == ".yaml":
            # Save the path to selection and enable the edit button
            self.query_one("#selection", Label).update(str(event.path))
            self._selection = event.path
            self.query_one("#edit_resource", Button).disabled = False

            # Enable the bump button if the resource is frozen otherwise make
            # sure it is disabled.
            if self._manager[event.path].frozen:
                self.query_one("#bump_resource", Button).disabled = False
            else:
                self.query_one("#bump_resource", Button).disabled = True
        else:
            # Not a resource file, so reset the selection and disable the buttons
            self.query_one("#selection", Label).update("")
            self._selection = None
            self.query_one("#edit_resource", Button).disabled = True
            self.query_one("#bump_resource", Button).disabled = True

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """
        Handle the selection of a directory in the directory tree.
            -> does not use the @on decorator, because the event itself needs to
               be queried for the path to the selected file.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `directory_tree_directory_selected`, which
              is the snake case version of the message type with periods
              replaced with underscores. e.g. `textual.widget.DirectoryTree.DirectorySelected` object.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.

        Effects
        -------
        - Set `_selection` to None.
        - Disable the edit_resource button.
        - Disable the bump_resource button.
        """
        self.query_one("#selection", Label).update("")
        self._selection = None
        self.query_one("#edit_resource", Button).disabled = True
        self.query_one("#bump_resource", Button).disabled = True

    @on(Button.Pressed, "#new_resource")
    def handle_new_resource(self) -> None:
        """
        Handle the press of the new resource button.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "bump_resource".

        Effects
        -------
        - Post a message to the app to display the BumpScreen.
        """

        self.post_message(self.NewScreen(self._manager))

    @on(Button.Pressed, "#edit_resource")
    def handle_edit_resource(self) -> None:
        """
        Handle the press of the edit resource button.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "edit_resource".

        Effects
        -------
        - Post a message to the app to display the EditScreen for the selected resource.
        """
        # Sanity check to ensure that the update path is set
        if self._selection is None:
            raise RuntimeError("Edit resource button pressed, but no resource selected for editing.")

        self.post_message(self.StartEdit(self._manager[self._selection]))

    @on(Button.Pressed, "#bump_resource")
    def handle_bump_resource(self) -> None:
        """
        Handle the press of the bump resource button.
        ---> `@on` decorator says that this method will be called when a Button.Pressed event is
             triggered on a button with the id "bump_resource".

        Effects
        -------
        - Post a message to the app to display the BumpScreen.
        """
        # Sanity check to ensure that the update path is set
        if self._selection is None:
            raise RuntimeError("Bump resource button pressed, but no resource selected for bumping.")

        self.post_message(self.BumpScreen(self._selection, self._manager))

    def on_manager_complete(self, event: Manager.Complete) -> None:
        """
        Handle the the completion message from the manager after an operation.
        ---> This is posted by the manager when an operation is complete.

        Effects
        -------
        - Disables the bump resource button if the operation unfroze the selected
          resource, as now the resource should now be unlocked and no longer in
          need of a bump.
        - Reloads the manager to reflect the changes made by the bump operation.
          (updates the icons and such)
        """
        self._manager.reload()
        match event.state:
            case BumpScreen.Return.BUMP:
                if not (self._selection and self._manager[self._selection].frozen):
                    self.query_one("#bump_resource", Button).disabled = True

            case NewScreen.Return.CREATE:
                # If a new resource was created, reload the manager to reflect the changes
                pass

            case BumpScreen.Return.EDIT:
                # If the resource was edited, reload the manager to reflect the changes
                pass
