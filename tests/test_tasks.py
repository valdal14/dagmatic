from dagmatic.core.task import Task, TaskState


def test_task_initial_state():
    t = Task(id="extract_snowflake")
    assert t.state == TaskState.PENDING
    assert len(t.upstream_ids) == 0
    assert len(t.downstream_ids) == 0


def test_task_add_relationships():
    t1 = Task(id="task_1")

    t1.add_downstream("task_2")
    t1.add_upstream("task_0")

    # Test that the sets are populated
    assert "task_2" in t1.downstream_ids
    assert "task_0" in t1.upstream_ids

    # Test idempotency (Sets should prevent duplicates)
    t1.add_downstream("task_2")
    assert len(t1.downstream_ids) == 1
