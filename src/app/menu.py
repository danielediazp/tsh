import logging
from collections import OrderedDict
from threading import Event, Thread
import time

import readchar
from rich.console import Console
from rich.live import Live
from rich.text import Text

from utils.csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex
from utils.constant import PAGER_TOP, PAGER_BOTTOM, ENTER, UP_K, DOWN_K, ENTER_K
from .task_form import TaskForm

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


class Menu:

    def __init__(
        self,
        csl: Console,
        fetch_data: callable,
        back: callable,
        add_new_state: callable,
    ):
        self.csl: Console = csl

        # Interactions
        self.back: callable = back

        # User Data
        self._items: OrderedDict = OrderedDict()
        self.fetch_data: callable = fetch_data
        self.add_new_state: callable = add_new_state
        # self.delete_item_by_id: callable = delete_item_by_id

        # Screen interactions handler attributes
        self._selected_option: int | None = None
        self._selected_idx: int = 0
        self._event: Event = Event()
        self._window_start: int = 0
        self._page_size: int = 10  # TODO: Make this user customizable
        self._slash_mode_on: bool = False
        self._slash_input: str = ""
        self._error_message: str | None = None

        self._load_data()

    def _load_data(self):
        items = self.fetch_data()
        self._items = OrderedDict({item.id: item for item in items})

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
        return f"[1-{len(self._items)}]"

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
        options = list(self._items.items())
        window_end = min(self._window_start + self._page_size, len(self._items))

        if self._window_start > 0:
            lines.append(PAGER_TOP)

        for i in range(self._window_start, window_end):
            item = options[i][1]
            if self._selected_idx == i:
                arrow = "→ " if show_arrow else "  "
                lines.append(
                    csl_str_factory(
                        f"{arrow} [{i + 1}] {item.title}",
                        CslStrStyleAttribute.BOLD,
                        ColorIndex(11),
                    )
                )
            else:
                lines.append(f"   [{i + 1}] {item.title}")

        if window_end < len(self._items):
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

    def _validate_selection(self, idx: int) -> bool:
        """Check if the user selected a valid task number of the one being display in the screen.

        Args:
            idx (int): The number representing the task that the user selected.

        Returns:
            bool: True if the number represents a valid display on the screen, False otherwise.
        """
        if 0 <= idx < len(self._items):
            self._error_message = None
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
        items = list(self._items.keys())
        self._selected_option = items[0]
        while not self._event.is_set():
            key = readchar.readkey()

            if not self._slash_mode_on:
                if key == "/":
                    self._error_message = None
                    self._slash_mode_on = True
                    self._slash_input = ""
                elif key == UP_K:
                    self._selected_idx = (self._selected_idx - 1) % len(self._items)
                    self._selected_option = items[self._selected_idx]
                elif key == DOWN_K:
                    self._selected_idx = (self._selected_idx + 1) % len(self._items)
                    self._selected_option = items[self._selected_idx]
                elif key in ENTER_K:
                    if self._selected_option is not None:
                        self._event.set()

            else:
                if key in ENTER_K:  # Enter: attempt to parse
                    try:
                        choice_idx = int(self._slash_input) - 1
                    except ValueError:
                        self._error_message = csl_str_factory(
                            f"The input must be a number within {self._get_menu_range()}",
                            color=ColorIndex(9),
                        )
                    else:
                        if self._validate_selection(choice_idx):
                            self._selected_idx = choice_idx
                            self._event.set()
                    self._slash_mode_on = False
                elif key in ("\x7f", "\b"):  # Backspace
                    self._slash_input = self._slash_input[:-1]
                elif key.isprintable():
                    self._slash_input += key

    def _display_menu(self) -> None:
        """
        Displays the menu until the user confirms a selection.
        Launches key listener and updates display via Live.
        Returns the selected key.
        """
        self._selected_option = next(iter(self._items))
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

    def run(self) -> None:
        # TODO: Open description tab
        # MENU -> user select valid option -> task description tab
        while True:
            self._display_menu()
            if self._selected_option:
                self.csl.clear()
                self.add_new_state(
                    TaskForm(self.csl, self.back, self._items[self._selected_option])
                )
            else:
                self.csl.clear()
