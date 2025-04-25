import sys
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console

from utils import singleton
from app import Menu
from exceptions import InvalidStateTransition


@singleton
@dataclass
class Tsh:
    """Singleton instance class used to represent the Task Shell CLI tool.
    This manages the transition between all the application states.

    Defines:
        back
        add_new_state
    """

    csl: Console
    state_manager: list[Any] = field(default_factory=list)

    def __post_init__(self):
        """Initialized the Tsh first state."""
        self.add_new_state(Menu(self.csl))

    def back(self) -> None:
        """Removes the current state and renders the previous state. This works as a transition
        back to previous console screen being display.

        Raises:
            InvalidStateTransition: If there's not previous state to transition to.
        """
        try:
            self.state_manager.pop()
            self.state_manager[-1].run()
        except IndexError:
            raise InvalidStateTransition

    def add_new_state(self, state: Any) -> None:
        """Add's new state to the Tsh and renders its content in the console. This servers as a transition
        from the current window to a new one.

        Args:
            state (Any): An object that must implement the run method to display content in the console.
        """
        self.state_manager.append(state)
        self.state_manager[-1].run()

    def exit(self):
        """Exist the Tsh gracefully."""
        sys.exit()
