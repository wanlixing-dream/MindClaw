from __future__ import annotations

import random
import time
import uuid

from mindclaw.scheduler.graph import TaskNode
from mindclaw.worker_pool.interface import WorkerBackend, WorkerHandle


class MockBackend(WorkerBackend):
    """Simulates task execution with random sleep. Always succeeds."""

    def __init__(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        self._min = min_seconds
        self._max = max_seconds
        self._start_times: dict[str, float] = {}
        self._durations: dict[str, float] = {}

    def execute(self, task: TaskNode) -> WorkerHandle:
        worker_id = f"mock-worker-{uuid.uuid4().hex[:6]}"
        handle = WorkerHandle(worker_id=worker_id, task_id=task.task_id)
        self._start_times[task.task_id] = time.monotonic()
        self._durations[task.task_id] = random.uniform(self._min, self._max)
        return handle

    def poll(self, handle: WorkerHandle) -> str:
        start = self._start_times.get(handle.task_id)
        duration = self._durations.get(handle.task_id)
        if start is None or duration is None:
            return "failed"
        elapsed = time.monotonic() - start
        if elapsed >= duration:
            handle.status = "completed"
            return "completed"
        return "running"

    def collect_result(self, handle: WorkerHandle) -> str:
        duration = self._durations.get(handle.task_id, 0)
        return f"[mock] Task {handle.task_id} completed by {handle.worker_id} in {duration:.1f}s"
