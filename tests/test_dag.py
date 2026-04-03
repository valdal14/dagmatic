import pytest

from dagmatic.core.dag import DAG, CyclicDependencyError
from dagmatic.core.task import Task


def test_add_task_raises_value_error():
    dag = DAG()
    dag.add_task(Task("A"))

    with pytest.raises(ValueError) as exc_info:
        dag.add_task(Task("A"))

    assert "Task ID 'A' already exists." in str(exc_info.value)


def test_add_dependency_raises_value_error_if_two_tasks_with_the_same_id_are_passed():
    dag = DAG()
    t1 = Task("A")
    dag.add_task(t1)

    with pytest.raises(ValueError) as exc_info:
        dag.add_dependency("A", "A")

    assert "A task cannot depend on itself." in str(exc_info.value)


def test_validate_and_sort():
    dag = DAG()
    t1, t2, t3 = Task("A"), Task("B"), Task("C")

    dag.add_task(t1)
    dag.add_task(t2)
    dag.add_task(t3)

    # A -> B -> C
    dag.add_dependency("A", "B")
    dag.add_dependency("B", "C")

    order = dag.validate_and_sort()
    assert order == ["A", "B", "C"]


def test_dag_cycle_detection():
    dag = DAG()
    t1, t2, t3 = Task("A"), Task("B"), Task("C")

    for t in [t1, t2, t3]:
        dag.add_task(t)

    # A -> B -> C -> A (Cycle!)
    dag.add_dependency("A", "B")
    dag.add_dependency("B", "C")
    dag.add_dependency("C", "A")

    with pytest.raises(CyclicDependencyError):
        dag.validate_and_sort()
