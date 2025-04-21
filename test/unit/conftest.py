import pytest

from utils.sql import SqlManager
from utils.models import Task, CompletedTask


TEST_DB = "sqlite:///:memory:"


@pytest.fixture(scope="package")
def sql_manager():
    manager = SqlManager(TEST_DB)
    yield manager
    manager.engine.dispose()


def drop_tables(sql_manager: SqlManager):
    with sql_manager.get_session() as session:
        session.query(Task).delete()
        session.query(CompletedTask).delete()


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
