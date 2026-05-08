from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskNode:
    task_id: str
    title: str
    description: str = ""
    depends_on: list[str] = field(default_factory=list)
    assigned_to: str = ""
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""


class CyclicDependencyError(Exception):
    pass


class DanglingDependencyError(Exception):
    pass


@dataclass
class TaskGraph:
    goal: str
    nodes: dict[str, TaskNode] = field(default_factory=dict)

    def add_node(self, node: TaskNode) -> None:
        self.nodes[node.task_id] = node

    def roots(self) -> list[TaskNode]:
        return [n for n in self.nodes.values() if not n.depends_on]

    def dependents(self, task_id: str) -> list[TaskNode]:
        return [
            n for n in self.nodes.values()
            if task_id in n.depends_on
        ]

    def all_completed(self) -> bool:
        return all(n.status == TaskStatus.COMPLETED for n in self.nodes.values())

    def has_failures(self) -> bool:
        return any(n.status == TaskStatus.FAILED for n in self.nodes.values())

    def validate(self) -> None:
        all_ids = set(self.nodes.keys())
        for node in self.nodes.values():
            for dep_id in node.depends_on:
                if dep_id not in all_ids:
                    raise DanglingDependencyError(
                        f"Task '{node.task_id}' depends on '{dep_id}' which does not exist."
                    )
        self._detect_cycles()

    def _detect_cycles(self) -> None:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {tid: WHITE for tid in self.nodes}

        def dfs(tid: str) -> None:
            color[tid] = GRAY
            for dep_tid in self.dependents(tid):
                c = color[dep_tid.task_id]
                if c == GRAY:
                    raise CyclicDependencyError(
                        f"Cycle detected involving task '{dep_tid.task_id}'."
                    )
                if c == WHITE:
                    dfs(dep_tid.task_id)
            color[tid] = BLACK

        for tid in self.nodes:
            if color[tid] == WHITE:
                dfs(tid)
