from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from mindclaw.scheduler.graph import TaskNode


@dataclass
class WorkerHandle:
    worker_id: str
    task_id: str
    status: str = "running"


class WorkerBackend(ABC):
    """Abstract interface for worker execution backends."""

    @abstractmethod
    def execute(self, task: TaskNode) -> WorkerHandle:
        """Start executing a task. Returns a handle for tracking."""

    @abstractmethod
    def poll(self, handle: WorkerHandle) -> str:
        """Check execution status. Returns 'running' | 'completed' | 'failed'."""

    @abstractmethod
    def collect_result(self, handle: WorkerHandle) -> str:
        """Collect the execution result summary after completion."""
