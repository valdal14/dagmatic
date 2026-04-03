from collections import deque

from dagmatic.core.task import Task


class CyclicDependencyError(Exception):
    """
    Raised when the DAG contains a circular dependency (e.g., A -> B -> A),
    which makes topological sorting mathematically impossible.
    """

    pass


class DAG:
    """
    The global registry and orchestrator for Tasks.

    This class maintains the in-memory representation of the Directed Acyclic Graph,
    manages the registration of tasks, draws the dependency edges between them,
    and executes topological sorting to determine the safe execution order.

    Attributes:
        tasks (dict[str, Task]): A dictionary mapping task IDs to their Task objects.
    """

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task) -> None:
        """
        Registers a new Task into the DAG.

        Args:
            task (Task): The Task object to add.

        Raises:
            ValueError: If a task with the exact same ID is already registered.
        """
        if task.id in self.tasks:
            raise ValueError(f"Task ID '{task.id}' already exists.")
        self.tasks[task.id] = task

    def add_dependency(self, upstream_id: str, downstream_id: str) -> None:
        """
        Creates a directed edge between two existing tasks in the DAG.

        Args:
            upstream_id (str): The ID of the prerequisite task.
            downstream_id (str): The ID of the dependent task.

        Raises:
            ValueError: If either task has not been added to the DAG first.
            ValueError: If the upstream and downstream IDs are identical (self-loop).
        """
        if upstream_id == downstream_id:
            raise ValueError("A task cannot depend on itself.")

        if upstream_id not in self.tasks or downstream_id not in self.tasks:
            raise ValueError("Both tasks must be added to the DAG before setting dependencies.")

        upstream_task = self.tasks[upstream_id]
        downstream_task = self.tasks[downstream_id]

        upstream_task.add_downstream(downstream_id)
        downstream_task.add_upstream(upstream_id)

    def validate_and_sort(self) -> list[str]:
        """
        Executes Kahn's Algorithm to topologically sort the DAG.

        Validates that the graph is strictly acyclic and calculates the linear
        mathematical order in which tasks must be executed to satisfy all dependencies.

        Returns:
            list[str]: An ordered list of task IDs representing the execution sequence.

        Raises:
            CyclicDependencyError: If a cycle is detected, making sorting impossible.
        """
        in_degrees: dict[str, int] = {}
        sorted_execution_order: list[str] = []
        queue: deque[str] = deque()

        # Build the in_degrees dictionary
        for task_id, task_obj in self.tasks.items():
            in_degrees[task_id] = len(task_obj.upstream_ids)

        # Find tasks with 0 dependencies and add to queue
        for task_id, degree in in_degrees.items():
            if degree == 0:
                queue.append(task_id)

        while len(queue) > 0:
            # Pop the first ID off the front of the queue
            current_id = queue.popleft()
            sorted_execution_order.append(current_id)

            # Fetch the actual task object to look at its downstream connections
            current_task = self.tasks.get(current_id)

            for downstream_id in current_task.downstream_ids:
                # Remove one dependency from the downstream task
                in_degrees[downstream_id] -= 1

                # If it has 0 dependencies left, it is unblocked and ready to run
                if in_degrees[downstream_id] == 0:
                    queue.append(downstream_id)

        # Cycle Detection Audit
        if len(sorted_execution_order) != len(self.tasks):
            raise CyclicDependencyError("Cycle detected in DAG. Infinite loop prevented.")

        return sorted_execution_order
