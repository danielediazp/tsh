import pytest
from unittest.mock import Mock

from app.menu import MainMenu
from app.task_form import TaskForm
from utils.constant import DOWN_K, ENTER_K, ADD_ITEM_ACTION, EXIT_PROG_ACTION


def test_load_data_populates_items(main_menu):
    assert list(main_menu.items.keys()) == [1, 2, 3]
    assert [t.title for t in main_menu.items.values()] == ["1", "2", "3"]


def test_get_menu_option_str_returns_title(main_menu):
    task = main_menu.items[2]
    assert main_menu.get_menu_option_str(task) == "2"


def test_validate_selection_sets_error_and_returns_correctly_ok(main_menu):
    main_menu._slash_input = "1"
    assert main_menu._validate_selection() is True
    assert main_menu._error_message is None


def test_validate_selection_sets_error_and_returns_correctly_error(main_menu):
    main_menu._slash_input = "10"
    ok = main_menu._validate_selection()
    assert ok is False
    assert "must be within [1-3]" in main_menu._error_message


def test_handle_selected_option_pushes_taskform(main_menu, mock_add_new_state):
    main_menu.handle_selected_option(main_menu.items[1])

    mock_add_new_state.assert_called_once()
    new_state = mock_add_new_state.call_args[0][0]
    assert isinstance(new_state, TaskForm)
    assert new_state.task.id == 1


def test_get_menu_markup_includes_tasks_and_instructions(main_menu):
    # arrow visible
    markup = main_menu._get_menu(show_arrow=True)
    assert "[1] 1" in markup
    assert "[2] 2" in markup
    assert "[3] 3" in markup
    assert "→" in markup

    # arrow hidden
    main_menu._selected_idx = 1
    markup_no_arrow = main_menu._get_menu(show_arrow=False)
    assert "→" not in markup_no_arrow
    assert "[1] 1" in markup
    assert "[2] 2" in markup
    assert "[3] 3" in markup


def test_display_and_selection_flow(
    monkeypatch, console, sample_tasks, mock_add_new_state
):
    keys = iter([DOWN_K, ENTER_K[0]])  # Simulated DOWN and ENTER keys
    monkeypatch.setattr("readchar.readkey", lambda: next(keys))

    menu = MainMenu(
        csl=console,
        fetch_data=Mock(return_value=sample_tasks),
    )
    assert list(menu.items.keys()) == [1, 2, 3]

    menu._display_menu()
    assert menu._event.is_set()
    menu.handle_selected_option(menu.items[menu._selected_option])

    new_state = mock_add_new_state.call_args[0][0]
    assert isinstance(new_state, TaskForm)


@pytest.mark.parametrize("action", [cmd for cmd in ADD_ITEM_ACTION])
def test_main_menu_add_action(monkeypatch, main_menu, mock_add_new_state, action):
    keys = iter(["/"] + [char for char in action] + [ENTER_K[0]])
    monkeypatch.setattr("readchar.readkey", lambda: next(keys))
    main_menu._display_menu()
    assert main_menu._event.is_set()
    assert main_menu._slash_input == action
    main_menu.handle_new_item()
    new_state = mock_add_new_state.call_args[0][0]
    assert isinstance(new_state, TaskForm)


@pytest.mark.parametrize("action", [cmd for cmd in EXIT_PROG_ACTION])
def test_main_menu_exit_prog_action(monkeypatch, main_menu, mock_exit, action):
    keys = iter(["/"] + list(action) + [ENTER_K[0]])
    monkeypatch.setattr("readchar.readkey", lambda: next(keys))

    main_menu._event.clear()
    main_menu._exec = True
    main_menu._key_listener()

    assert main_menu._event.is_set()
    assert main_menu._exec is False

    main_menu.run()

    mock_exit.assert_called_once()
