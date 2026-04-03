from enum import Enum


class TaskState(Enum):
    """
    Represents the current execution state of a Task within the DAG.
    """

    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3


class Task:
    """
    A single unit of work (node) within the Directed Acyclic Graph (DAG).

    This class tracks its own state and maintains references to its immediate
    upstream and downstream dependencies. It is decoupled from the global graph logic.

    Args:
        id (str): The unique identifier for this task.

    Attributes:
        id (str): The unique identifier for this task.
        state (TaskState): The current execution state of the task. Defaults to PENDING.
        upstream_ids (set): A set of task IDs that must complete before this task starts.
        downstream_ids (set): A set of task IDs that are waiting for this task to finish.
    """

    def __init__(self, id: str) -> None:
        self.id: str = id
        self.state: TaskState = TaskState.PENDING
        self.upstream_ids: set = set()
        self.downstream_ids: set = set()

    def add_downstream(self, task_id: str) -> None:
        """
        Registers a task that depends on the completion of this task.

        Args:
            task_id (str): The unique identifier of the dependent downstream task.
        """
        self.downstream_ids.add(task_id)

    def add_upstream(self, task_id: str) -> None:
        """
        Registers a prerequisite task that must complete before this task can begin.

        Args:
            task_id (str): The unique identifier of the required upstream task.
        """
        self.upstream_ids.add(task_id)
