from enum import Enum
from typing import Any, Callable


class TaskState(Enum):
    """
    Represents the current execution state of a Task within the DAG.
    """

    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3
    UPSTREAM_FAILED = 4


class Task:
    """
    A single unit of work (node) within the Directed Acyclic Graph (DAG).

    This class tracks its own state, maintains references to its dependencies,
    and securely executes its assigned callable workload.

    Attributes:
        id (str): The unique identifier for this task.
        target (Callable | None): The Python function to execute.
        args (tuple): Positional arguments passed to the target.
        kwargs (dict): Keyword arguments passed to the target.
        error (Exception | None): Stores the exception if the task fails.
        state (TaskState): The current execution state of the task.
        upstream_ids (set): A set of prerequisite task IDs.
        downstream_ids (set): A set of dependent task IDs.
    """

    def __init__(
        self,
        id: str,
        target: Callable[..., Any] | None = None,
        args: tuple = (),
        kwargs: dict | None = None,
    ) -> None:
        self.id: str = id
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.error: Exception | None = None
        self.state: TaskState = TaskState.PENDING
        self.upstream_ids: set[str] = set()
        self.downstream_ids: set[str] = set()

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

    def execute(self) -> None:
        """
        Executes the target callable safely within a state machine wrapper.

        Transitions the task from PENDING to RUNNING. If successful, transitions
        to SUCCESS. If an exception occurs, catches it, stores the trace in self.error,
        and transitions to FAILED.

        Raises:
            RuntimeError: If the task is not in the PENDING state prior to execution.
        """
        if self.state is not TaskState.PENDING:
            raise RuntimeError(f"Task '{self.id}' is not in PENDING state.")

        self.state = TaskState.RUNNING

        try:
            if self.target is not None:
                self.target(*self.args, **self.kwargs)

            self.state = TaskState.SUCCESS

        except Exception as e:
            self.error = e
            self.state = TaskState.FAILED
