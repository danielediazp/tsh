import logging
from collections import OrderedDict
from threading import Event, Thread
import time

import readchar
from rich.console import Console
from rich.live import Live
from rich.text import Text

from utils.csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex
from utils.models import Task

LOGGER = logging.getLogger(__name__)
ITEMS_ON_TOP = "...[previous items hidden]..."
ITEMS_ON_BOTTOM = "...[more items hidden]..."
INSTRUCTIONS = "'"


class Menu:

    ACTIONS = []

    def __init__(self, csl: Console):
        self.csl: Console = csl

        # User Data
        self._task: OrderedDict = OrderedDict()

        # Screen interactions handler attributes
        self._selected_idx: int = 0
        self._event: Event = Event()
        self._window_start: int = 0
        self._page_size: int = 0  # TODO: Make this user customizable
        self._slash_mode_on: int = False
        self._slash_input: str = ""

    def _update_window(self) -> None:
        """
        Adjusts the window_start so that the selected_index is always within the displayed page.
        """
        if self._selected_idx < self._window_start:
            self._window_start = self._selected_idx
        elif self._selected_idx >= self._window_start + self._page_size:
            self._window_start = self._selected_idx - self._page_size + 1

    def get_menu(self, show_arrow: bool) -> str:
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
        options = list(self._task.items())
        window_end = min(self._window_start + self._page_size, len(self._task))

        if self._window_start > 0:
            lines.append(ITEMS_ON_TOP)

        for i in range(self._window_start, window_end):
            task: Task = options[i]
            if self._selected_idx == i:
                arrow = "→ " if show_arrow else "  "
                lines.append(
                    csl_str_factory(f"{arrow} [{i}] {task.title}"),
                    CslStrStyleAttribute.BOLD,
                    ColorIndex(11),
                )
            else:
                lines.append(f"   [{i}] {task.title}")

        if window_end < len(lines):
            lines.append(ITEMS_ON_BOTTOM)

    def _key_listener(self) -> None:
        pass

    def _display_menu(self) -> str:
        pass

    def _go_back(self) -> None:
        pass

    def run(self) -> None:
        pass
