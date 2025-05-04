import pytest
import time
from datetime import datetime
from unittest.mock import patch

from rich.console import Console
from unittest.mock import Mock

from utils.sql import SqlManager
from utils.models import Task, History
from app.menu import MainMenu


TEST_DB = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """
    Disable all real sleeps in tests by patching time.sleep to a fast no-op.
    """
    monkeypatch.setattr(time, "sleep", lambda *args, **kwargs: None)


@pytest.fixture(scope="package")
def sql_manager():
    manager = SqlManager(TEST_DB)
    yield manager
    manager.engine.dispose()


def drop_tables(sql_manager: SqlManager):
    with sql_manager.get_session() as session:
        session.query(Task).delete()
        session.query(History).delete()


@pytest.fixture
def clean_db(sql_manager: SqlManager):
    drop_tables(sql_manager)
    yield sql_manager
    drop_tables(sql_manager)


@pytest.fixture
def dummy_task(clean_db):
    t = Task(title="some", description="some")
    clean_db.insert(t)
    yield t


class DummyConsole(Console):
    """A class use to mock the `rich.console` object.

    This class records clear() calls without touching the real terminal.
    """

    def __init__(self):
        super().__init__(record=True)
        self.clear_calls = 0
        self.print_calls = []

    def clear(self):
        self.clear_calls += 1

    def print(self, *args, **kwargs):
        self.print_calls.append((args, kwargs))


@pytest.fixture
def sample_tasks():
    return [
        Task(id=1, title="1", description="1", created_at=datetime.now()),
        Task(id=2, title="2", description="2", created_at=datetime.now()),
        Task(id=3, title="3", description="3", created_at=datetime.now()),
    ]


@pytest.fixture
def console():
    yield DummyConsole()


@pytest.fixture
def main_menu(sample_tasks, console):
    fetch_data = Mock(return_value=sample_tasks)
    yield MainMenu(
        csl=console,
        fetch_data=fetch_data,
    )


class DummyLive:
    """Class use as a stub for `rich.live` object

    This class prevent any real rendering from happening in the terminal.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def update(self, *args, **kwargs):
        # no real rendering
        pass


@pytest.fixture
def dummy_live():
    yield DummyLive


@pytest.fixture
def mock_add_new_state():
    with patch("app.app.TshStates.add_new_state") as p:
        yield p


@pytest.fixture
def mock_back():
    with patch("app.app.TshStates.back") as p:
        yield p
