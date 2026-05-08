from __future__ import annotations

from mindclaw.scheduler.graph import TaskNode
from mindclaw.worker_pool.interface import WorkerBackend, WorkerHandle


class WorkerPool:
    """Manages worker dispatch and polling across concurrent tasks."""

    def __init__(self, backend: WorkerBackend, max_workers: int = 4) -> None:
        self._backend = backend
        self._max_workers = max_workers
        self._active: dict[str, WorkerHandle] = {}  # task_id → handle

    def dispatch(self, task: TaskNode) -> WorkerHandle:
        handle = self._backend.execute(task)
        task.assigned_to = handle.worker_id
        self._active[task.task_id] = handle
        return handle

    def poll_all(self) -> dict[str, str]:
        results: dict[str, str] = {}
        for task_id, handle in list(self._active.items()):
            status = self._backend.poll(handle)
            results[task_id] = status
            if status in ("completed", "failed"):
                self._active.pop(task_id, None)
        return results

    def collect_result(self, task_id: str) -> str:
        handle = self._active.get(task_id)
        if handle is None:
            # Handle already removed after poll — reconstruct from backend
            return f"[pool] No active handle for {task_id}"
        return self._backend.collect_result(handle)

    def active_count(self) -> int:
        return len(self._active)

    def can_accept(self) -> bool:
        return len(self._active) < self._max_workers
