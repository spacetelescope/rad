"""
This module provides the app's functionality for bumping RAD resource versions
--> There are two Textual widgets:
    1. Bump: A widget that handles the list of resources to be bumped.
    2. BumpTab: The TabPane for the App that allows the user to select a resource to bump.

--> There is also a BumpScreen that is a Textual Screen that overlays the main app
    and allows the user to go through the process of deciding the new versions for the
    resources to be bumped.
"""

from __future__ import annotations

from collections.abc import Generator
from graphlib import TopologicalSorter

from astropy.utils import lazyproperty
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.messages import Message

from ._resource import Resource

__all__ = ("Bump",)


class _Bump:
    """
    This class handles the data needed to bump a given RAD resource

    This performs several tasks:
    1. It builds a dependency graph for the resource and its bump updates.
        - This is done to ensure that when the resource bumps occur, there is only
          one update per managed resource (otherwise, the managed resources may
          loose their updates).
        - This is done via recursing through all the bump updates for the resource
          rather than just immediately working out the full collection of bump updates.
          This is done so that the graph can be established using the subgraphs of
          each bump update.
    2. It provides the generator through which the updates can be applied in the
       order determined by the dependency graph.

    Parameters
    ----------
    resource : Resource
        The resource that is the target of the bump updates.
    generator : Generator[_Bump, None, None]
        A generator that yields the _Bump instance for each direct update that
        needs to be applied to the resource.
    """

    def __init__(self, resource: Resource, generator: Generator[_Bump, None, None]) -> None:
        self.resource = resource
        self._generator = generator

    @lazyproperty
    def _bumps(self) -> dict[str, _Bump]:
        """
        Store the results from the generator so that they can be reused.
        """
        return {update.resource.uri: update for update in self._generator}

    @lazyproperty
    def resources(self) -> dict[str, Resource]:
        """
        This flushes out the actual resource objects that will have bump updates
        """
        # Start with the target resource
        resources = {
            self.resource.uri: self.resource,
        }

        # Add in resources derived from each of the bumps
        for bump in self._bumps.values():
            resources.update(bump.resources)

        return resources

    @lazyproperty
    def graph(self) -> dict[str, set[str]]:
        """
        Build the dependency graph for updating the resource.
        --> Graph format
            vertex (uri) -> set of vertices (uri) that depend on it
        """
        graph = {self.resource.uri: set(self._bumps.keys())}
        for bump in self._bumps.values():
            for vertex, edge in bump.graph.items():
                if vertex in graph:
                    graph[vertex].update(edge)
                else:
                    graph[vertex] = edge

        return graph

    @lazyproperty
    def _order(self) -> tuple[str]:
        """
        Get the update order for the schema.
        --> this is the order in which the resources should be looped through

        By construction of the graph, this will place the ultimate target resource
        as the last item in the ordering, so that later body updates in the manager
        can be applied without worrying about conflicts with the resource being
        stored within this object.
        """
        return tuple(TopologicalSorter(self.graph).static_order())

    @lazyproperty
    def _uris(self) -> set[str]:
        """
        Get the URIs for the resources in the update.
        """
        return set(self.resources.keys())

    def bump(self, bump_versions: dict[str, str]) -> Generator[Resource, None, None]:
        """
        Generator that bumps each resource and yields the resulting "bumped" resource.
        """
        if self._uris != set(bump_versions.keys()):
            raise RuntimeError("Attempting to bump an incomplete update.")

        for uri in self._order:
            yield self.resources[uri].bump(bump_versions[uri])


class Bump(_Bump, VerticalScroll):
    """
    The class that acts to handle the bumping of a given RAD resource inside the Textual app,
    by mixing the _Bump class with the VerticalScroll (container) widget.

    ---> Acts as a container for each of the resource widgets that are to be bumped.
         It is specifically "scrollable" so that the user can scroll through a particularly
         long list of resources that are to be bumped.

         ^
         | <last resource widget in ordering>
         |
         scrollable
         |
         | <first resource widget in ordering>
         v

         The ordering is specifically so that the resource actually being bumped is at the top
         though when the bumps are applied, it will be the last resource to be bumped
    """

    class Ready(Message):
        """
        Message to be posted by the Bump widget when all resources have a valid version entered for
        bumping.

        --> The message contents is what is needed to perform the bump operation inside the app.

        Parameters
        ----------
        bump: Generator[Resource, None, None]
            A generator that yields the a bumped resource
        """

        def __init__(self, bump: Generator[Resource, None, None]) -> None:
            super().__init__()
            self.bump = bump

    def __init__(self, resource: Resource, generator: Generator[_Bump, None, None], *args, **kwargs) -> None:
        super().__init__(resource, generator)
        super(_Bump, self).__init__(*args, **kwargs)

        # Do some initial setup
        self._set_label_width()
        self._bump_versions: dict[str, str] = {}  # Storage for the outputs of the Resource widgets

    def compose(self) -> ComposeResult:
        """
        Compose (render in the App) the bump widget
        ---> Scrollable vertical container of Resource Widgets
        """
        # Note: reverse order so main target resource for bumping is at the top
        for uri in self._order[::-1]:
            yield self.resources[uri]

    def _set_label_width(self) -> None:
        """
        Find and set a common label width for all the resources to be bumped.
        ---> Makes sure the input boxes are aligned vertically in the UI to make
             it easier to follow
        ---> the rad_app.tcss file has some CSS to ensure that this looks passible
             on the screen.
        """
        width = 0
        for uri in self._order[::-1]:
            if width < self.resources[uri].label_width:
                width = self.resources[uri].label_width

        for resource in self.resources.values():
            resource.label_width = width

    def reset(self) -> Generator[None, None, None]:
        """
        Reset the the resources in the update.
        ---> Basically, this is called to make sure that the resources are reset
             in the manager with no changes if the users decides not to initiate
             a bump operation.
        """
        for resource in self.resources.values():
            resource.reset_width()
            yield

    def on_resource_bump(self, event: Resource.Bump) -> None:
        """
        Handles the messages sent by the Resource widgets for each resource displayed
        in the Bump widget when the user enters a valid new version number.

        --> Textual wires stuff together based on names:
            - `on_` prefix is a signal to Textual that this is a event handler.
            - Next part is the event type, in this case `resource_bump`, which
              is the snake case version of the message type with periods
              replaced with underscores i.e. `Resource.Bump` message.
        --> Textual will wire this into the app and call this whenever the the
            event is triggered.

        Events are passed upwards through the application, so this will only be
        triggered if the event occurs in this widget or one of its children.
        ---> In this case, this will be triggered by any of the Resource widgets

        Effects
        -------
        - Save the result of the `Resource.Bump` message to the `_bump_versions` dict
        - If all resources have been filled in, post a `Bump.Ready` message
        """
        # Stop the event from propagating further up the widget tree
        event.stop()

        # Store the bump version for the resource
        self._bump_versions[event.resource.uri] = event.bump_version

        # If all resources have been filled in, post a Bump.Ready message
        if self._uris == set(self._bump_versions.keys()):
            # Notice the this is passing the generator out
            self.post_message(self.Ready(self.bump(self._bump_versions)))
