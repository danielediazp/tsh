import logging
from collections import OrderedDict
from threading import Event, Thread
import time

import readchar
from rich.console import Console
from rich.live import Live
from rich.text import Text

from utils import singleton

LOGGER = logging.getLogger(__name__)


@singleton
class Menu:

    ACTIONS = []

    def __init__(self, csl: Console):
        self.task: OrderedDict = OrderedDict()
        self.csl: Console = csl
        self.selected_idx: int = 0
        self.event: Event = Event()

    def get_menu(self, show_arrow: bool) -> Text:
        options = []
        for idx, (_, obj) in enumerate(self.task):
            if self.selected_idx == idx:
                arrow = "→ " if show_arrow else ""
                option = f"{arrow}[bold yellow][{idx}] {obj}[/bold yellow]"
            else:
                option = f"   [{idx}] {obj}"

            options.append(option)

        return "\n".join(options)

    def key_listener(self) -> None:
        pass

    def display_menu(self) -> str:
        pass

    def go_back(self) -> None:
        pass

    def run(self) -> None:
        pass
