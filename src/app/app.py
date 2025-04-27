import sys
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console

from utils.decorators import singleton
from utils.models import Task
from app.menu import MainMenu
from exceptions import InvalidStateTransition


# TODO: Get rid of this, this is a func for UI testing purposes.
def fetch_task_data():
    from datetime import datetime

    """
    A sample function that fetches data from the database and returns a list of Task objects.
    """
    tasks = [
        Task(id=i, title=f"Task {i}", description="some", created_at=datetime.now())
        for i in range(25)
    ]
    return tasks


@singleton
@dataclass
class Tsh:
    """Singleton class representing the Task Shell (Tsh) CLI application.

    This class manages the lifecycle and transitions between different application states
    (e.g., menus, forms) within the Task Shell CLI. It maintains a stack-based state manager
    to handle navigation, ensuring smooth transitions between views.

    Upon initialization, the `MainMenu` is loaded as the initial state.

    Attributes:
        csl (Console): Rich console instance used for rendering content.
        state_manager (list[Any]): Stack of application states. Each state is expected to implement a `run()` method.

    Methods:
        back(): Transition back to the previous state.
        add_new_state(state): Push a new state onto the stack and render it.
        exit(): Exit the application gracefully.
    """

    csl: Console
    state_manager: list[Any] = field(default_factory=list)

    def __post_init__(self):
        """Initialized the Tsh first state."""
        self.add_new_state(
            MainMenu(
                csl=self.csl,
                fetch_data=fetch_task_data,
                back=self.back,
                add_new_state=self.add_new_state,
            )
        )

    def back(self) -> None:
        """Transition back to the previous state in the state manager.

        Pops the current state from the stack and runs the previous state.
        Ensures the user can navigate backward in the application.

        Raises:
            InvalidStateTransition: If there is no previous state to transition to.
        """
        try:
            self.state_manager.pop()
            self.state_manager[-1].run()
        except IndexError:
            raise InvalidStateTransition

    def add_new_state(self, state: Any) -> None:
        """Push a new state onto the state manager stack and render it.

        This method transitions the application to a new view by adding the provided
        state object (which must implement a `run()` method) and invoking it.

        Args:
            state (Any): The new application state. Must implement a `run()` method for rendering.
        """
        self.state_manager.append(state)
        self.state_manager[-1].run()

    def exit(self):
        """Exist the Tsh gracefully."""
        sys.exit()
