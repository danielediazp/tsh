import pytest

from sqlalchemy.exc import SQLAlchemyError

from utils.models import Task, TaskStatus


def test_insert_task_model_with_description(clean_db):
    # GIVEN
    title = "Daily Task"
    description = "This is some description that the user can provide."
    t = Task(title=title, description=description)

    # WHEN
    clean_db.insert(t)

    # THEN
    row = clean_db.query(Task, single=True)
    assert row.id == 1
    assert row.title == title
    assert row.description == description
    assert row.created_at is not None
    assert row.completed_at is None
    assert not row.is_deleted
    assert row.status == TaskStatus.ACTIVE
    assert not len(row.history)


def test_task_unique_ids(clean_db, dummy_task):
    # GIVEN
    t = Task(id=1, title="some")

    # WHEN / THEN
    with pytest.raises(SQLAlchemyError):
        clean_db.insert(t)

    assert len(clean_db.query(Task)) == 1


def test_insert_task_duplicates_with(clean_db):
    # GIVEN
    title1 = "some"
    title2 = "some2"
    t1 = Task(title=title1)
    t2 = Task(title=title2)

    # WHEN
    clean_db.insert([t1, t2])  # we allow for duplicates task by default

    # THEN
    rows = clean_db.query(Task)
    assert len(rows) == 2
    assert [entry.id for entry in rows] == [1, 2]
    assert [entry.title for entry in rows] == [title1, title2]
    assert all(entry.created_at is not None for entry in rows)
    assert all(entry.completed_at is None for entry in rows)
    assert all(entry.status == TaskStatus.ACTIVE for entry in rows)
    assert all(not entry.is_deleted for entry in rows)
