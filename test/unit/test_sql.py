import pytest

from sqlalchemy.exc import SQLAlchemyError

from utils.models import Task, History, TaskStatus
from utils.sql import SqlManager


def test_sql_manager(clean_db: SqlManager):
    # All rows should be empty
    assert clean_db.query(Task) == []
    assert clean_db.query(History) == []


def test_sql_manager_insert_single_element(clean_db):
    # GIVEN
    title = "Some Task"
    task = Task(title=title)

    # WHEN
    clean_db.insert(task)

    # THEN
    row = clean_db.query(Task, single=True)
    assert row.title == title
    assert row.id == 1
    assert row.description is None
    assert row.created_at is not None
    assert row.completed_at is None
    assert not row.is_deleted
    assert row.status == TaskStatus.ACTIVE
    assert not len(row.history)


def test_psql_manager_insert_list_same_element(clean_db):
    # GIVEN
    title1 = "t1"
    title2 = "t2"
    entries = [Task(title=title1), Task(title=title2)]

    # WHEN
    clean_db.insert(entries)

    # THEN
    rows = clean_db.query(Task)
    assert [entry.id for entry in rows] == [1, 2]
    assert [entry.title for entry in rows] == [title1, title2]
    assert all(entry.created_at is not None for entry in rows)
    assert all(entry.completed_at is None for entry in rows)
    assert all(entry.status == TaskStatus.ACTIVE for entry in rows)
    assert all(not entry.is_deleted for entry in rows)


def test_sql_manager_exception_raise(clean_db):
    # GIVEN
    hist = History(task_id=1)  # Should fail task_id if a Fk

    # WHEN / THEN
    with pytest.raises(SQLAlchemyError) as e:
        clean_db.insert(hist)


def test_sql_manager_update(clean_db, dummy_task):
    # GIVEN
    new_desc = "New Description"

    # WHEN
    clean_db.update(Task, dummy_task.id, description=new_desc)

    # THEN
    row = clean_db.query(Task, single=True)
    assert row.title == dummy_task.title
    assert row.description != dummy_task.description
    assert row.description == new_desc
    assert row.created_at is not None
    assert row.completed_at is None
    assert not row.is_deleted
    assert row.status == TaskStatus.ACTIVE
    assert not len(row.history)


def test_sql_manager_delete_one_entry(clean_db, dummy_task):
    # GIVEN/ WHEN
    clean_db.delete(Task, id=dummy_task.id)

    # THEN
    assert clean_db.query(Task) == []


def test_sql_manager_delete_multiple_entry(clean_db):
    # GIVEN
    t1 = Task(title="1")
    t2 = Task(title="1")
    clean_db.insert([t1, t2])

    # WHEN
    clean_db.delete(Task, title="1")

    # THEN
    assert clean_db.query(Task) == []


def test_sql_manager_delete_multiple_entry_but_not_all(clean_db):
    # GIVEN
    t1 = Task(title="1")
    t2 = Task(title="1")
    t3 = Task(title="2")
    clean_db.insert([t1, t2, t3])

    # WHEN
    clean_db.delete(Task, title="1")

    # THEN
    rows = clean_db.query(Task)
    assert len(rows) == 1
    assert rows[0].title == "2"
