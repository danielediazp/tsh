from utils.models import CompletedTask, Task


def test_completed_task_relation_on_insert(clean_db, dummy_task):
    # GIVEN
    ct = CompletedTask(task_id=dummy_task.id)

    # WHEN
    clean_db.insert(ct)

    # THEN
    row = clean_db.query(CompletedTask, single=True)
    assert row.id == 1
    assert row.task_id == dummy_task.id
    assert row.task.title == dummy_task.title
    assert row.task.description == dummy_task.description
    assert row.task.creation_datetime == dummy_task.creation_datetime


def test_completed_task_relation_on_update(clean_db, dummy_task):
    # GIVEN
    ct = CompletedTask(task_id=dummy_task.id)

    # WHEN
    clean_db.insert(ct)
    t = clean_db.update(Task, dummy_task.id, description="New Description")

    # THEN
    row = clean_db.query(CompletedTask, single=True)
    assert row.id == 1
    assert row.task_id == t.id
    assert row.task.title == t.title
    assert row.task.description == t.description
    assert row.task.creation_datetime == t.creation_datetime


def test_completed_task_relation_on_delete(clean_db, dummy_task):
    # GIVEN
    ct = CompletedTask(task_id=dummy_task.id)

    # WHEN
    clean_db.insert(ct)
    clean_db.delete(Task, id=dummy_task.id)

    # THEN : It should CASCADE UP
    assert clean_db.query(CompletedTask) == []


def test_completed_task_relation_on_delete_multiple(clean_db):
    # GIVEN
    ts = [Task(title="1"), Task(title="1"), Task(title="2")]
    clean_db.insert(ts)

    cts = [CompletedTask(task_id=t.id) for t in ts]
    clean_db.insert(cts)

    # WHEN
    clean_db.delete(Task, title="1")

    # THEN
    rows = clean_db.query(CompletedTask)
    assert len(rows) == 1
    assert rows[0].task_id == ts[-1].id
