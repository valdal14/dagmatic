import asyncio
import time

import pytest

from dagmatic.core.dag import DAG
from dagmatic.core.task import Task, TaskState


def success_func() -> bool:
    return True


def failing_func() -> None:
    raise ValueError("Simulated Extraction Failure")


def test_dag_successful_execution():
    dag = DAG()
    t1 = Task("A", target=success_func)
    t2 = Task("B", target=success_func)

    dag.add_task(t1)
    dag.add_task(t2)
    dag.add_dependency("A", "B")

    dag.execute()

    assert t1.state == TaskState.SUCCESS
    assert t2.state == TaskState.SUCCESS


def test_dag_cascade_failure():
    dag = DAG()
    # A (Fails) -> B (Should be UPSTREAM_FAILED) -> C (Should be UPSTREAM_FAILED)
    # D (Independent, Should SUCCEED)
    tA = Task("A", target=failing_func)
    tB = Task("B", target=success_func)
    tC = Task("C", target=success_func)
    tD = Task("D", target=success_func)

    for t in [tA, tB, tC, tD]:
        dag.add_task(t)

    dag.add_dependency("A", "B")
    dag.add_dependency("B", "C")

    dag.execute()

    # Check the root failure
    assert tA.state == TaskState.FAILED
    assert isinstance(tA.error, ValueError)

    # Check the cascade
    assert tB.state == TaskState.UPSTREAM_FAILED
    assert tC.state == TaskState.UPSTREAM_FAILED

    # Check that independent branches still run
    assert tD.state == TaskState.SUCCESS


async def slow_async_success() -> bool:
    # Simulates waiting for AWS/Snowflake
    await asyncio.sleep(0.1)
    return True


@pytest.mark.asyncio
async def test_dag_async_parallel_execution():
    dag = DAG()
    # B and C should run simultaneously. Total time ~1 second, not 2.
    tA = Task("A", target=slow_async_success)
    tB = Task("B", target=slow_async_success)
    tC = Task("C", target=slow_async_success)

    for t in [tA, tB, tC]:
        dag.add_task(t)

    dag.add_dependency("A", "B")
    dag.add_dependency("A", "C")

    start_time = time.time()
    await dag.execute_async()
    end_time = time.time()

    duration = end_time - start_time

    assert tA.state == TaskState.SUCCESS
    assert tB.state == TaskState.SUCCESS
    assert tC.state == TaskState.SUCCESS

    # Confirms they ran concurrently (if sync, it would take ~3 seconds)
    assert duration < 2.5
