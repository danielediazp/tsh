import sys
from dataclasses import dataclass
from typing import Any, ClassVar

from utils.decorators import singleton
from exceptions import InvalidStateTransition


class TshStates:
    """Singleton class representing the States of Task Shell (Tsh) CLI application.

    This class manages the lifecycle and transitions between different application states
    (e.g., menus, forms) within the Task Shell CLI. It maintains a stack-based state manager
    to handle navigation, ensuring smooth transitions between views.

    Attributes:
        csl (Console): Rich console instance used for rendering content.
        state_manager (list[Any]): Stack of application states. Each state is expected to implement a `run()` method.

    Methods:
        back(): Transition back to the previous state.
        add_new_state(state): Push a new state onto the stack and render it.
        exit(): Exit the application gracefully.
    """

    state_manager: ClassVar[list[Any]] = []

    @classmethod
    def back(cls) -> None:
        """Transition back to the previous state in the state manager.

        Pops the current state from the stack and runs the previous state.
        Ensures the user can navigate backward in the application.

        Raises:
            InvalidStateTransition: If there is no previous state to transition to.
        """
        try:
            cls.state_manager.pop()
            cls.state_manager[-1].run()
        except IndexError:
            raise InvalidStateTransition

    @classmethod
    def add_new_state(cls, state: Any) -> None:
        """Push a new state onto the state manager stack and render it.

        This method transitions the application to a new view by adding the provided
        state object (which must implement a `run()` method) and invoking it.

        Args:
            state (Any): The new application state. Must implement a `run()` method for rendering.
        """
        cls.state_manager.append(state)
        cls.state_manager[-1].run()

    @staticmethod
    def exit():
        """Exist the Tsh gracefully."""
        sys.exit()
