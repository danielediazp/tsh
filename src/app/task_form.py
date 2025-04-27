from threading import Event, Thread
import time
import json
import readchar
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.json import JSON

from utils.models import Task
from utils.csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex
from utils.constant import UP_K, DOWN_K, RIGHT_K, LEFT_K, ENTER_K, BACK_K
from utils.date import get_date

TITLE = "Title"
DESC = "Description"
TITLE_INPUT_HOLDER = csl_str_factory("Enter title...", CslStrStyleAttribute.ITALIC)
DESC_INPUT_HOLDER = csl_str_factory("Enter description...", CslStrStyleAttribute.ITALIC)
BLINKER = csl_str_factory("|", CslStrStyleAttribute.BOLD, ColorIndex(2))
VIEW_EDIT_FORM_HEADER = csl_str_factory("VIEW/EDIT Form", CslStrStyleAttribute.BOLD, ColorIndex(5))
ADD_FORM_HEADER = csl_str_factory("ADD Form", CslStrStyleAttribute.BOLD, ColorIndex(5))


class TaskForm:
    """A form for collecting user information with Title and Description fields."""

    def __init__(self, csl: Console, back: callable, some_task: Task = None):
        # Handle app state interactions
        self.back: callable = back

        self.csl: Console = csl

        # Data to display in the form
        self.task: Task = some_task
        self._created_at: str | None = None
        self.current_field: int = 0  # 0 for Title; 1 for Description
        self.fields: list[str] = [
            "",
            "",
        ]  # fields[0] holds Title, fields[1] holds Description
        self.cursor_pos: list[int] = [
            0,
            0,
        ]  # Keeps track of cursor position for each field
        self.selection_event: Event = Event()

        if some_task is not None:
            title = some_task.title
            desc = some_task.description or ""
            self.fields = [title, desc]
            self.cursor_pos = [len(title), len(desc)]
            self._created_at = get_date(self.task.created_at)

    def _get_form_header(self) -> str:
        """Gets the proper header for the form depending on the mode that it was access.

        Returns:
            str: The header of the string.
        """
        if self.task is not None:
            return f"{VIEW_EDIT_FORM_HEADER} Created at: {self._created_at}"
        else:
            return ADD_FORM_HEADER
        
    def _render_form(self) -> Group:
        """Builds and returns the rendered form as a Rich Group.

        Returns:
            Group: A group containing the header, field panels, and instructions.
        """
        header = Panel(
            Text.from_markup(self._get_form_header(), justify="center"),
            title="Form",
            border_style="bright_blue",
            padding=(1, 2),
            title_align="center",
        )

        title_content = self.fields[0] if self.fields[0] != "" else TITLE_INPUT_HOLDER
        desc_content = self.fields[1] if self.fields[1] != "" else DESC_INPUT_HOLDER

        title_panel = self._build_field_panel(title_content, TITLE, 0)
        desc_panel = self._build_field_panel(desc_content, DESC, 1)

        # instructions = Text(
        #     "Type to add characters. Use [bold]Backspace[/bold] to delete. Use [bold]Up[/bold] and [bold]Down[/bold] arrows to change field.\n"
        #     "Use [bold]Left[/bold] and [bold]Right[/bold] arrows to move within the field.\n"
        #     "In the Title field, press [bold]Enter[/bold] to move to Description; in the Description field, press [bold]Enter[/bold] to submit.",
        #     style="dim"
        # )

        return Group(
            header,
            title_panel,
            desc_panel,
            # instructions
        )

    def _build_field_panel(self, content: str, title: str, field_index: int) -> Panel:
        """Helper method to build the field panel with proper highlighting.

        Args:
            content (str): The content of the field.
            title (str): The title of the field (e.g., "Title" or "Description").
            field_index (int): The index of the current field (0 for Title, 1 for Description).

        Returns:
            Panel: A Rich Panel containing the field content and title.
        """
        # TODO: this should be user configurable
        border_style = "bold green" if self.current_field == field_index else "white"
        displayed_content = self._insert_cursor(content, self.cursor_pos[field_index])
        return Panel(
            displayed_content, title=title, border_style=border_style, padding=(1, 2)
        )

    def _insert_cursor(self, content: str, cursor_pos: int) -> str:
        """Helper method to insert a cursor at the appropriate position in the content.

        Args:
            content (str): The content of the field.
            cursor_pos (int): The current position of the cursor.

        Returns:
            str: The content with the cursor inserted at the specified position.
        """
        text_before_cursor = content[:cursor_pos]
        text_after_cursor = content[cursor_pos:]
        return f"{text_before_cursor}{BLINKER}{text_after_cursor}"

    def _key_listener(self):
        """Listen for key input and update the form state.

        This method handles key presses for navigating the fields, typing, and deleting characters.
        """
        while not self.selection_event.is_set():
            key = readchar.readkey()

            if key == UP_K:
                self.current_field = (self.current_field - 1) % 2
            elif key == DOWN_K:
                self.current_field = (self.current_field + 1) % 2
            elif key == RIGHT_K:
                if self.cursor_pos[self.current_field] < len(
                    self.fields[self.current_field]
                ):
                    self.cursor_pos[self.current_field] += 1
            elif key == LEFT_K:
                if self.cursor_pos[self.current_field] > 0:
                    self.cursor_pos[self.current_field] -= 1
            elif key in ENTER_K:
                if self.current_field == 0:
                    self.current_field = 1
                else:
                    self.selection_event.set()

            #  Backspace erases from what every field the user is currently on
            elif key in BACK_K:
                if (
                    self.fields[self.current_field]
                    and self.cursor_pos[self.current_field] > 0
                ):
                    self.fields[self.current_field] = (
                        self.fields[self.current_field][
                            : self.cursor_pos[self.current_field] - 1
                        ]
                        + self.fields[self.current_field][
                            self.cursor_pos[self.current_field] :
                        ]
                    )
                    self.cursor_pos[self.current_field] -= 1

            # Case valid key that can be added to the test
            else:
                self.fields[self.current_field] = (
                    self.fields[self.current_field][
                        : self.cursor_pos[self.current_field]
                    ]
                    + key
                    + self.fields[self.current_field][
                        self.cursor_pos[self.current_field] :
                    ]
                )
                self.cursor_pos[self.current_field] += 1

    def _start_key_listener(self):
        """Start the key listener in a background thread."""
        listener_thread = Thread(target=self._key_listener, daemon=True)
        listener_thread.start()

    def _display_form(self):
        """Use Live to continuously update the form."""
        with Live(self._render_form(), console=self.csl, refresh_per_second=10) as live:
            while not self.selection_event.is_set():
                live.update(self._render_form())
                time.sleep(0.1)

    def submit_form(self):
        """Prepare and print the final JSON output."""
        # TODO: If the title or the description is different from the original update it in the db.
        data = {"title": self.fields[0], "description": self.fields[1]}
        json_str = json.dumps(data, indent=4)
        self.csl.print(JSON(json_str))
        self.back()

    def run(self):
        """Main execution method for the form."""
        self._start_key_listener()
        self._display_form()
        self.csl.clear()
        self.submit_form()
