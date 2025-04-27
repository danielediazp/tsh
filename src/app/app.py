import sys
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console

from utils.decorators import singleton
from utils.models import Task
from app.menu import Menu
from exceptions import InvalidStateTransition


# TODO: Get rid of this, this is a func for UI testing purposes.
def fetch_task_data():
    from datetime import datetime
    """
    A sample function that fetches data from the database and returns a list of Task objects.
    """
    tasks = [Task(id=i, title=f"Task {i}", description="some", created_at=datetime.now()) for i in range(25)]
    return tasks


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
        self.add_new_state(
            Menu(
                csl=self.csl,
                fetch_data=fetch_task_data,
                back=self.back,
                add_new_state=self.add_new_state,
            )
        )

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
