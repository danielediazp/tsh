import logging
from collections import OrderedDict
from threading import Event, Thread
import time
from abc import ABC, abstractmethod
from typing import Any, override
from collections.abc import Callable

import readchar
from rich.console import Console
from rich.live import Live
from rich.text import Text

from utils.csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex
from utils.constant import (
    PAGER_TOP,
    PAGER_BOTTOM,
    ENTER,
    UP_K,
    DOWN_K,
    ENTER_K,
    BACK_K,
    ADD_ITEM_ACTION,
    EXIT_PROG_ACTION,
)
from utils.models import Task
from .task_form import TaskForm
from utils.decorators import singleton
from .app import TshStates

LOGGER = logging.getLogger(__name__)

MENU_INSTRUCTIONS = (
    "\n\n"
    + " Press "
    + csl_str_factory("/", CslStrStyleAttribute.BOLD, ColorIndex(9))
    + " to enter action mode. Or use "
    + csl_str_factory("UP | DOWN", CslStrStyleAttribute.BOLD, ColorIndex(9))
    + " arrows and "
    + ENTER
)


class Menu(ABC):
    """Abstract base class for interactive terminal menus.

    This class provides the core logic for displaying a paginated, navigable menu in a terminal
    using the Rich library. It handles user interactions such as keyboard input (arrow keys,
    enter, slash commands) and maintains selection state, pagination, and error handling.

    Subclasses are required to:
        - Load and populate menu items via `load_data`.
        - Define how each item should be displayed via `get_menu_option_str`.
        - Implement the logic for handling the selected option via `handle_selected_option`.
        - Define how to add new items to the menu if add_new_item is enable via `handle_new_item` \
            this method should be override since by default `Menu` doesn't support adding new items.

    Attributes:
        csl (Console): Rich console instance for rendering the menu.
        _items (OrderedDict): The ordered set of menu items (key-value pairs).
        _selected_option (int | None): The currently selected item key.
        _selected_idx (int): The index of the selected item in the ordered list.
        _event (Event): Threading event to control user input and menu rendering.
        _window_start (int): The index of the first item in the current paginated window.
        _page_size (int): Number of items to display per page (default is 10).
        _slash_mode_on (bool): Indicates whether the user is in slash input mode.
        _slash_input (str): The current input buffer for slash mode.
        _error_message (str | None): Error message to display (if any).
        add_new_item (bool): True if new obj should handle adding a new item to the item list, False otherwise. Defaults to Fault.
    """

    def __init__(
        self,
        csl: Console,
        add_item_enable: bool = False,
    ):
        self.csl: Console = csl

        # User Data
        self.items: OrderedDict = OrderedDict()

        # Screen interactions handler attributes
        self._selected_option: int | None = 0
        self._selected_idx: int = 0
        self._event: Event = Event()
        self._window_start: int = 0
        self._page_size: int = 10  # TODO: Make this user customizable
        self._slash_mode_on: bool = False
        self._slash_input: str = ""
        self._error_message: str | None = None
        self.add_item_enable = add_item_enable
        self.add_new_item: bool = False

        # Flag for the current screen to keep rendering
        self._exec: bool = True

        self.load_data()

    @abstractmethod
    def load_data(self) -> None:
        """Load and populate the menu items.

        This method must be implemented by subclasses to populate the `items` attribute
        with the appropriate data. `items` should be an `OrderedDict` where keys are
        unique identifiers, and values are the data associated with each menu option.
        """
        pass

    @abstractmethod
    def get_menu_option_str(self, item: Any) -> str:
        """Return the string representation for a given menu item.

        This method defines how each item should be displayed in the menu.

        Args:
            item (Any): The data associated with a menu option.

        Returns:
            str: The formatted string to display for the given item.
        """
        pass

    def _update_window(self) -> None:
        """
        Adjusts the window_start so that the selected_index is always within the displayed page.
        """
        if self._selected_idx < self._window_start:
            self._window_start = self._selected_idx
        elif self._selected_idx >= self._window_start + self._page_size:
            self._window_start = self._selected_idx - self._page_size + 1

    def _get_menu_range(self) -> str:
        """Gets the range of options in the menu as str.

        Returns:
            str: a str in the format [<UPPER BOUND> - <LOWER BOUND>]
        """
        return f"[1-{len(self.items)}]"

    def _get_menu(self, show_arrow: bool) -> str:
        """Build the paginated menu markup string.

        A blinking arrow is shown next to the selected option. If in slash mode,
        appends the listening prompt and current input buffer.

        Args:
            show_arrow (bool): True if the arrow should be visible, False otherwise.

        Returns:
            str: Menu to be display in the console.
        """
        self._update_window()
        lines = []
        options = list(self.items.items())
        window_end = min(self._window_start + self._page_size, len(self.items))

        if self._window_start > 0:
            lines.append(PAGER_TOP)

        for i in range(self._window_start, window_end):
            item = options[i][1]
            title = self.get_menu_option_str(item)
            if self._selected_idx == i:
                arrow = "→ " if show_arrow else "  "
                lines.append(
                    csl_str_factory(
                        f"{arrow} [{i + 1}] {title}",
                        CslStrStyleAttribute.BOLD,
                        ColorIndex(11),
                    )
                )
            else:
                lines.append(f"   [{i + 1}] {title}")

        if window_end < len(self.items):
            lines.append(PAGER_BOTTOM)

        menu_txt = "\n".join(lines)
        menu_txt += MENU_INSTRUCTIONS
        if self._slash_mode_on:
            menu_txt += (
                "\n\n"
                + csl_str_factory(
                    "Selection Mode: ", CslStrStyleAttribute.BOLD, ColorIndex(9)
                )
                + f"Enter a number {self._get_menu_range()} and press "
                + ENTER
                + "\n >"
                + f"{self._slash_input}"
            )

        if self._error_message:
            menu_txt += "\n\n" + self._error_message

        return menu_txt

    def _validate_selection(self) -> bool:
        """Check if the user selected a valid task number of the one being display in the screen.

        Args:
            idx (int): The number representing the task that the user selected.

        Returns:
            bool: True if the number represents a valid display on the screen, False otherwise.
        """
        try:
            idx = int(self._slash_input) - 1
        except ValueError:
            return False

        if 0 <= idx < len(self.items):
            self._error_message = None
            self._selected_idx = idx
            return True

        self._error_message = csl_str_factory(
            f"The number must be within {self._get_menu_range()}", color=ColorIndex(9)
        )
        return False

    def _key_listener(self) -> None:
        """Listens for key input in a background thread.

        Handles:
            - '/' to enter slash mode.
            - In slash mode: builds slash_input, handles backspace and enter for validation.
            - Outside slash mode: Up/Down arrows to move selection, Enter to confirm.
        """
        items = list(self.items.keys())

        while not self._event.is_set():
            key = readchar.readkey()

            if not self._slash_mode_on:
                if key == "/":
                    self._error_message = None
                    self._slash_mode_on = True
                    self._slash_input = ""
                elif key == UP_K:
                    self._selected_idx = (self._selected_idx - 1) % len(self.items)
                    self._selected_option = items[self._selected_idx]
                elif key == DOWN_K:
                    self._selected_idx = (self._selected_idx + 1) % len(self.items)
                    self._selected_option = items[self._selected_idx]
                elif key in ENTER_K:
                    LOGGER.info("selected option on enter %s", self._selected_option)
                    if self._selected_option is not None:
                        self._event.set()

            else:

                if key in ENTER_K:  # Enter: attempt to parse
                    if self.add_item_enable and self._slash_input in ADD_ITEM_ACTION:
                        self._selected_option = None
                        self.add_new_item = True
                        self._event.set()

                    elif self._slash_input in EXIT_PROG_ACTION:
                        self._selected_option = None
                        self._event.set()
                        self._exec = False

                    elif self._validate_selection():
                        self._event.set()
                        self._selected_option = items[self._selected_idx]
                    self._slash_mode_on = False
                elif key in BACK_K:  # Backspace
                    self._slash_input = self._slash_input[:-1]
                elif key.isprintable():
                    self._slash_input += key

    def _display_menu(self) -> None:
        """
        Displays the menu until the user confirms a selection.
        Launches key listener and updates display via Live.
        Returns the selected key.
        """
        self._event.clear()

        listener: Thread = Thread(target=self._key_listener, daemon=True)
        listener.start()

        show_arrow = True
        with Live(console=self.csl, refresh_per_second=10) as live:
            while not self._event.is_set():
                menu_txt = self._get_menu(show_arrow)
                live.update(Text.from_markup(menu_txt, justify="left"))
                show_arrow = not show_arrow
                time.sleep(0.1)

        listener.join(timeout=0.1)
        self.csl.clear()

    @abstractmethod
    def handle_selected_option(self, selected_option: Any) -> None:
        """Handle the logic when a menu option is selected.

        This method is triggered when the user confirms a selection. It must be
        implemented by subclasses to define the action taken for the selected item.

        Args:
            selected_option (Any): The data associated with the selected menu option.
        """
        pass

    def handle_new_item(self):
        """Handles adding a new item to the item list.

        This method should be override by the Subclass if adding_new_item is enable. By default,
        this is not implemented.
        """
        pass

    def run(self) -> None:
        while self._exec:
            self._display_menu()
            self.csl.clear()
            if self._selected_option is not None:
                self.handle_selected_option(self.items[self._selected_option])
            elif self.add_item_enable and self.add_new_item:
                self.add_new_item = False
                self.handle_new_item()

        TshStates.exit()


@singleton
class MainMenu(Menu):
    """Main menu for displaying and interacting with a list of tasks.

    This class extends the `Menu` base class, providing concrete implementations
    for loading tasks, rendering their display strings, and handling task selection.

    The menu supports navigating through tasks, selecting a task to view or edit,
    and integrating with an application state manager for transitioning between views.

    Args:
        csl (Console): Rich console instance used for rendering the menu.
        fetch_data (Callable[[], list[Task]]): A callable that retrieves the list of tasks to display.

    Attributes:
        fetch_data (Callable[[], list[Task]]): Retrieves the current list of tasks.
    """

    def __init__(
        self,
        csl: Console,
        fetch_data: Callable[[None], list[Task]],
    ):
        self.fetch_data = fetch_data
        super().__init__(csl, True)

        # Default the selected option as the first item in the menu
        self._selected_option = next(iter(self.items)) if self.items else None

    def load_data(self) -> None:
        """Load the list of tasks into the menu.

        Fetches tasks using the `fetch_data` callable and populates the `items`
        attribute with task IDs as keys and `Task` objects as values.
        """
        items: list[Task] = self.fetch_data()
        self.items = OrderedDict({item.id: item for item in items})

    def get_menu_option_str(self, item: Task) -> str:
        """Get the string representation of a task for menu display.

        Args:
            item (Task): The task object to display.

        Returns:
            str: The task title to render in the menu.
        """
        return item.title

    def handle_selected_option(self, selected_option: Task) -> None:
        """Handle logic for when a task is selected from the menu.

        When a user selects a task, this method transitions to the `TaskForm`
        view for that task by adding it as a new state.

        Args:
            selected_option (Task): The selected task object.
        """
        self._transition_to_task_form(selected_option)

    def _transition_to_task_form(self, task: Task = None) -> None:
        """Transition from `MainMenu` to `TaskForm`.

        Args:
            task (Task, optional): The task to display if VIEW/EDIT mode otherwise None. Defaults to None.
        """
        TshStates.add_new_state(TaskForm(self.csl, task))

    @override
    def handle_new_item(self):
        """Handles adding a new item to the item list."""
        self._transition_to_task_form()
