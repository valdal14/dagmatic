import pytest

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


def dummy_function(x: int, y: int) -> int:
    return x + y


def failing_function():
    raise ValueError("Simulated network failure")


@pytest.mark.asyncio
async def test_task_execution_success():
    t = Task(id="math_task", target=dummy_function, args=(5, 3))

    await t.execute()

    assert t.state == TaskState.SUCCESS
    assert t.error is None


@pytest.mark.asyncio
async def test_task_execution_failure():
    t = Task(id="fail_task", target=failing_function)

    await t.execute()

    assert t.state == TaskState.FAILED
    assert isinstance(t.error, ValueError)


@pytest.mark.asyncio
async def test_task_cannot_execute_twice():
    task_name = "run_twice"
    t = Task(id=task_name, target=dummy_function, args=(1, 1))
    await t.execute()

    with pytest.raises(RuntimeError) as exc_info:
        await t.execute()

    assert f"Task '{task_name}' is not in PENDING state." in str(exc_info.value)
