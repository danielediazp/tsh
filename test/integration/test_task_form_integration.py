import pytest
from datetime import datetime
from unittest.mock import Mock

# from rich.panel import Panel
from rich.console import Group

from app.task_form import TaskForm
from utils.models import Task
from utils.constant import (
    ENTER_K,
    UP_K,
    DOWN_K,
    LEFT_K,
    RIGHT_K,
    BACK_K,
)
from app.task_form import (
    BLINKER,
    ADD_FORM_HEADER,
    VIEW_EDIT_FORM_HEADER,
    INSTRUCTIONS,
)


@pytest.fixture
def task_form_add_mode(console):
    yield TaskForm(csl=console, some_task=None)


@pytest.fixture
def title():
    return "Hello"


@pytest.fixture
def desc():
    return "World!"


@pytest.fixture
def dt_str():
    return "01/01/2025"


@pytest.fixture
def task_form_vd_mode(console, title, desc):
    created = datetime(2025, 1, 1, 12, 0)
    task = Task(id=42, title=title, description=desc, created_at=created)
    yield TaskForm(csl=console, some_task=task)


def test_task_form_init_add_mode(task_form_add_mode):
    form = task_form_add_mode

    assert form.fields == ["", ""]
    assert form.cursor_pos == [0, 0]
    assert form._created_at is None


def test_task_form_add_mode_header(task_form_add_mode):
    form = task_form_add_mode
    header = form._get_form_header()
    assert header == ADD_FORM_HEADER


def test_task_form_add_mode_render(task_form_add_mode):
    form = task_form_add_mode
    group: Group = form._render_form()
    header = group.renderables[0].renderable.plain
    assert "ADD Form" == header
    instructions = group.renderables[-1]
    assert INSTRUCTIONS == instructions


def test_task_form_init_view_edit_mode(task_form_vd_mode, title, desc, dt_str):
    form = task_form_vd_mode
    assert form.fields == [title, desc]
    assert form.cursor_pos == [len(title), len(desc)]
    assert form._created_at == dt_str


def test_task_view_edit_mode_header(task_form_vd_mode, dt_str):
    form = task_form_vd_mode
    header = form._get_form_header()
    assert VIEW_EDIT_FORM_HEADER in header
    assert f"Task Created at: {dt_str}" in header


def test_insert_cursor_behavior(task_form_vd_mode):
    form = task_form_vd_mode
    content = "ABCDEF"

    s = form._insert_cursor(content, 3)
    assert s == content[:3] + BLINKER + content[3:]


def test_run_full_flow(console, dummy_live, monkeypatch, task_form_add_mode, mock_back):
    """
    Simulate:
        - typing "Hi" for the title
        - Enter → move to description
        - typing "Desc"
        - Enter → submit
    Confirm that:
        - form.fields updated
        - console.clear called
        - back() called once
    """
    monkeypatch.setattr(
        "app.task_form.Live", dummy_live
    )  # stub out Live so no real rendering

    # build a key sequence:
    # 'H','i', ENTER → move to desc, 'D','e','s','c', ENTER → submit
    seq = ["H", "i", ENTER_K[0], "D", "e", "s", "c", ENTER_K[0]]
    key_iter = iter(seq)
    monkeypatch.setattr("readchar.readkey", lambda: next(key_iter))

    form = task_form_add_mode

    form.run()

    assert form.fields == ["Hi", "Desc"]
    assert console.clear_calls == 1
    mock_back.assert_called_once()


def test_backspace_and_navigation(console, dummy_live, monkeypatch, task_form_add_mode, mock_back):
    """
    Simulate:
        - typing 'XYZ'
        - Backspace twice (leaving 'X')
        - RIGHT, arrow movement
        - Enter
        - typing 'dp'
        - left arrow movement
        - typing a
        - Enter to submit form
    Check that:
        - editing and cursor movement behave as expected
    """
    monkeypatch.setattr("app.task_form.Live", dummy_live)

    # Build sequence:
    # 'X','Y','Z', BACK, BACK → leaves 'X'
    # RIGHT (no-op, at end), LEFT → cursor back
    # ENTER → switch to desc
    # 'd' 'p', LEFT, 'a' → leaves 'dap'
    # ENTER → submit immediately (desc stays "")
    seq = [
        "X",
        "Y",
        "Z",
        BACK_K[0],
        BACK_K[0],
        RIGHT_K,
        ENTER_K[0],
        "d",
        "p",
        LEFT_K,
        "a",
        ENTER_K[0],
    ]
    key_iter = iter(seq)
    monkeypatch.setattr("readchar.readkey", lambda: next(key_iter))

    form = task_form_add_mode
    form.run()

    assert form.fields == ["X", "dap"]
    mock_back.assert_called_once()
    assert console.clear_calls == 1


# TODO: Modify this test once DB connection is added. Task requires an title field.
def test_arrow_navigation_with_no_text(
    console, dummy_live, monkeypatch, task_form_add_mode, mock_back
):
    """
    Simulates:
        - Type arrow down
        - type error up
        - type error down
        - Enter to submit an empty form
    Check that:
        - The user can navigate through the form with the arrow keys
    """
    monkeypatch.setattr(
        "app.task_form.Live", dummy_live
    )  # stub out Live so no real rendering

    seq = [DOWN_K, UP_K, DOWN_K, ENTER_K[0]]
    key_iter = iter(seq)
    monkeypatch.setattr("readchar.readkey", lambda: next(key_iter))

    form = task_form_add_mode
    form.run()

    assert form.fields == ["", ""]
    mock_back.assert_called_once()
    assert console.clear_calls == 1
