from dagmatic.core.task import Task


def test_task_init():
    t = Task(id="extract_data")

    assert t is not None
    assert t.id == "extract_data"
