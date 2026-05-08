from __future__ import annotations

from mindclaw.scheduler.graph import TaskGraph, TaskNode, TaskStatus


class Scheduler:
    """Topological scheduler that yields ready task batches from a TaskGraph."""

    def __init__(self, graph: TaskGraph) -> None:
        self._graph = graph
        graph.validate()

    def get_ready_tasks(self) -> list[TaskNode]:
        completed_ids = {
            tid for tid, n in self._graph.nodes.items()
            if n.status == TaskStatus.COMPLETED
        }
        ready = []
        for node in self._graph.nodes.values():
            if node.status != TaskStatus.PENDING:
                continue
            if all(dep in completed_ids for dep in node.depends_on):
                ready.append(node)
        return ready

    def mark_running(self, task_id: str) -> None:
        self._graph.nodes[task_id].status = TaskStatus.RUNNING

    def mark_completed(self, task_id: str) -> None:
        self._graph.nodes[task_id].status = TaskStatus.COMPLETED

    def mark_failed(self, task_id: str) -> None:
        self._graph.nodes[task_id].status = TaskStatus.FAILED

    def is_finished(self) -> bool:
        for node in self._graph.nodes.values():
            if node.status in (TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.READY):
                return False
        return True

    def has_failed(self) -> bool:
        return self._graph.has_failures()

    @property
    def graph(self) -> TaskGraph:
        return self._graph
