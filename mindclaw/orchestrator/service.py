from __future__ import annotations

import time
from pathlib import Path

from mindclaw.decomposer.interface import DecomposerBase
from mindclaw.orchestrator.models import OrchestrationResult, OrchestrationStatus
from mindclaw.scheduler.engine import Scheduler
from mindclaw.scheduler.graph import TaskStatus
from mindclaw.tracker import Tracker
from mindclaw.worker_pool.interface import WorkerBackend
from mindclaw.worker_pool.manager import WorkerPool


class Orchestrator:
    """Pipeline orchestrator: decompose → schedule → dispatch → track."""

    def __init__(
        self,
        decomposer: DecomposerBase,
        worker_backend: WorkerBackend,
        max_workers: int = 4,
        poll_interval: float = 0.5,
        state_dir: Path | None = None,
    ) -> None:
        self._decomposer = decomposer
        self._backend = worker_backend
        self._max_workers = max_workers
        self._poll_interval = poll_interval
        self._state_dir = state_dir

    def run(self, goal: str, on_progress: callable = None) -> OrchestrationResult:
        start_time = time.monotonic()

        # 1. Decompose goal into task graph
        graph = self._decomposer.decompose(goal)
        graph.validate()

        # 2. Initialize scheduler, pool, tracker
        scheduler = Scheduler(graph)
        pool = WorkerPool(self._backend, self._max_workers)
        tracker = Tracker(graph)

        if on_progress:
            on_progress(tracker.summary())

        # 3. Main scheduling loop
        while not scheduler.is_finished():
            # Dispatch ready tasks
            ready = scheduler.get_ready_tasks()
            for task in ready:
                if pool.can_accept():
                    handle = pool.dispatch(task)
                    scheduler.mark_running(task.task_id)
                    tracker.update(task.task_id, TaskStatus.RUNNING)

            # Poll worker statuses
            statuses = pool.poll_all()
            for task_id, status in statuses.items():
                if status == "completed":
                    scheduler.mark_completed(task_id)
                    tracker.update(task_id, TaskStatus.COMPLETED, f"Task {task_id} done")
                elif status == "failed":
                    scheduler.mark_failed(task_id)
                    tracker.update(task_id, TaskStatus.FAILED, f"Task {task_id} failed")

            if on_progress:
                on_progress(tracker.summary())

            # Save intermediate state
            if self._state_dir:
                tracker.save(self._state_dir / "state.json")

            time.sleep(self._poll_interval)

        # 4. Final result
        elapsed = time.monotonic() - start_time
        final_status = (
            OrchestrationStatus.COMPLETED
            if not scheduler.has_failed()
            else OrchestrationStatus.FAILED
        )

        if self._state_dir:
            tracker.save(self._state_dir / "state.json")

        return OrchestrationResult(
            goal=goal,
            status=final_status,
            snapshot=tracker.snapshot(),
            elapsed_seconds=elapsed,
        )
