import pytest

from sqlalchemy.exc import SQLAlchemyError

from utils.models import Task


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
    assert row.creation_datetime


def test_task_unique_ids(clean_db, dummy_task):
    # GIVEN
    t = Task(id=1, title="some")

    # WHEN / THEN
    with pytest.raises(SQLAlchemyError):
        clean_db.insert(t)

    assert len(clean_db.query(Task)) == 1


def test_insert_task_duplicates_with(clean_db):
    # GIVEN
    t1 = Task(title="some")
    t2 = Task(title="some2")

    # WHEN
    clean_db.insert([t1, t2])  # we allow for duplicates task by default

    # THEN
    rows = clean_db.query(Task)
    assert len(rows) == 2
    assert [entry.id for entry in rows] == [1, 2]
    assert all(entry.creation_datetime is not None for entry in rows)
