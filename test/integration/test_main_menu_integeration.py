from unittest.mock import Mock

from app.menu import MainMenu
from app.task_form import TaskForm
from utils.constant import DOWN_K, ENTER_K


def test_load_data_populates_items(main_menu):
    assert list(main_menu._items.keys()) == [1, 2, 3]
    assert [t.title for t in main_menu._items.values()] == ["1", "2", "3"]


def test_get_menu_option_str_returns_title(main_menu):
    task = main_menu._items[2]
    assert main_menu.get_menu_option_str(task) == "2"


def test_validate_selection_sets_error_and_returns_correctly_ok(main_menu):
    assert main_menu._validate_selection(0) is True
    assert main_menu._error_message is None


def test_validate_selection_sets_error_and_returns_correctly_error(main_menu):
    ok = main_menu._validate_selection(10)
    assert ok is False
    assert "must be within [1-3]" in main_menu._error_message


def test_handle_selected_option_pushes_taskform(main_menu):
    main_menu.add_new_state.reset_mock()
    main_menu.handle_selected_option(main_menu._items[1])

    main_menu.add_new_state.assert_called_once()
    new_state = main_menu.add_new_state.call_args[0][0]
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


def test_display_and_selection_flow(monkeypatch, console, sample_tasks, dummy_live):
    monkeypatch.setattr(
        "app.menu.Live", dummy_live
    )  # Stub out Live to prevent real rendering

    keys = iter([DOWN_K, ENTER_K[0]])  # Simulated DOWN and ENTER keys
    monkeypatch.setattr("readchar.readkey", lambda: next(keys))

    selected = None

    def fake_add(state):
        nonlocal selected
        """Helper function to capture out the Task been pushed into the state."""
        selected = state

    menu = MainMenu(
        csl=console,
        fetch_data=Mock(return_value=sample_tasks),
        back=Mock(),
        add_new_state=fake_add,
    )

    assert list(menu._items.keys()) == [1, 2, 3]

    menu._display_menu()
    assert menu._event.is_set()
    menu.handle_selected_option(menu._items[menu._selected_option])

    assert console.clear_calls > 0
    assert isinstance(selected, TaskForm)
    assert selected.task.id == 2
