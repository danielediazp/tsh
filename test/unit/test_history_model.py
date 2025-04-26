from utils.models import Task, History


def test_history_relation_on_insert(clean_db, dummy_task):
    # GIVEN
    old_des = "some"
    new_des = "some"
    hist = History(
        task_id=dummy_task.id, old_description=old_des, new_description=new_des
    )

    # WHEN
    clean_db.insert(hist)

    # THEN
    row = clean_db.query(History, single=True)
    assert row.id == 1
    assert row.timestamp is not None
    assert row.task_id == dummy_task.id
    assert row.old_description == old_des
    assert row.new_description == new_des
    assert row.task.title == dummy_task.title
    assert row.task.description == dummy_task.description
    assert row.task.created_at == dummy_task.created_at
    assert row.task.completed_at == dummy_task.completed_at
    assert row.task.status == dummy_task.status

    t = clean_db.query(Task, single=True, id=dummy_task.id)
    assert row.id == t.history[0].id
    assert row.old_description == t.history[0].old_description
    assert row.new_description == t.history[0].new_description
    assert row.timestamp == t.history[0].timestamp


def test_history_relation_on_update(clean_db, dummy_task):
    # GIVEN
    old_des = "some"
    new_des = "some"
    hist = History(
        task_id=dummy_task.id, old_description=old_des, new_description=new_des
    )

    # WHEN
    clean_db.insert(hist)
    t = clean_db.update(Task, dummy_task.id, description="New Description")

    # THEN
    row = clean_db.query(History, single=True)
    assert row.id == 1
    assert row.task_id == t.id
    assert row.task.title == t.title
    assert row.task.description == t.description
    assert row.task.created_at == t.created_at


def test_history_relation_on_delete(clean_db, dummy_task):
    # GIVEN
    old_des = "some"
    new_des = "some"
    hist = History(
        task_id=dummy_task.id, old_description=old_des, new_description=new_des
    )

    # WHEN
    clean_db.insert(hist)
    clean_db.delete(Task, id=dummy_task.id)

    # THEN : It should CASCADE UP
    assert clean_db.query(History) == []


def test_history_relation_on_delete_multiple(clean_db):
    # GIVEN
    ts = [Task(title="1"), Task(title="1"), Task(title="2")]
    clean_db.insert(ts)

    old_des = "some"
    new_des = "some"
    hists = [
        History(task_id=t.id, old_description=old_des, new_description=new_des)
        for t in ts
    ]
    clean_db.insert(hists)

    # WHEN
    clean_db.delete(Task, title="1")

    # THEN
    rows = clean_db.query(History)
    assert len(rows) == 1
    assert rows[0].task_id == ts[-1].id
