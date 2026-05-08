"""Tests for the orchestration pipeline: decomposer, scheduler, worker pool, tracker, orchestrator."""

from __future__ import annotations

import pytest

from mindclaw.decomposer import MockDecomposer
from mindclaw.orchestrator.models import OrchestrationStatus
from mindclaw.orchestrator.service import Orchestrator
from mindclaw.scheduler.engine import Scheduler
from mindclaw.scheduler.graph import (
    CyclicDependencyError,
    DanglingDependencyError,
    TaskGraph,
    TaskNode,
    TaskStatus,
)
from mindclaw.tracker import Tracker
from mindclaw.worker_pool import MockBackend, WorkerPool


# ── TaskGraph ──────────────────────────────────────────────────────

class TestTaskGraph:
    def test_roots(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        g.add_node(TaskNode(task_id="B", title="B", depends_on=["A"]))
        assert [n.task_id for n in g.roots()] == ["A"]

    def test_dependents(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        g.add_node(TaskNode(task_id="B", title="B", depends_on=["A"]))
        g.add_node(TaskNode(task_id="C", title="C", depends_on=["A"]))
        deps = g.dependents("A")
        assert sorted(n.task_id for n in deps) == ["B", "C"]

    def test_validate_dangling(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A", depends_on=["Z"]))
        with pytest.raises(DanglingDependencyError):
            g.validate()

    def test_validate_cycle(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A", depends_on=["B"]))
        g.add_node(TaskNode(task_id="B", title="B", depends_on=["A"]))
        with pytest.raises(CyclicDependencyError):
            g.validate()

    def test_validate_clean(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        g.add_node(TaskNode(task_id="B", title="B", depends_on=["A"]))
        g.validate()  # should not raise


# ── Scheduler ──────────────────────────────────────────────────────

class TestScheduler:
    def _make_graph(self) -> TaskGraph:
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        g.add_node(TaskNode(task_id="B", title="B", depends_on=["A"]))
        g.add_node(TaskNode(task_id="C", title="C", depends_on=["A"]))
        g.add_node(TaskNode(task_id="D", title="D", depends_on=["B", "C"]))
        return g

    def test_initial_ready(self):
        s = Scheduler(self._make_graph())
        ready = s.get_ready_tasks()
        assert [t.task_id for t in ready] == ["A"]

    def test_parallel_after_root(self):
        s = Scheduler(self._make_graph())
        s.mark_running("A")
        s.mark_completed("A")
        ready = s.get_ready_tasks()
        assert sorted(t.task_id for t in ready) == ["B", "C"]

    def test_final_ready(self):
        s = Scheduler(self._make_graph())
        s.mark_running("A")
        s.mark_completed("A")
        s.mark_running("B")
        s.mark_completed("B")
        s.mark_running("C")
        s.mark_completed("C")
        ready = s.get_ready_tasks()
        assert [t.task_id for t in ready] == ["D"]

    def test_is_finished(self):
        s = Scheduler(self._make_graph())
        assert not s.is_finished()
        for tid in ["A", "B", "C", "D"]:
            s.mark_running(tid)
            s.mark_completed(tid)
        assert s.is_finished()

    def test_has_failed(self):
        s = Scheduler(self._make_graph())
        s.mark_running("A")
        s.mark_failed("A")
        assert s.has_failed()


# ── MockDecomposer ─────────────────────────────────────────────────

class TestMockDecomposer:
    def test_returns_valid_graph(self):
        d = MockDecomposer()
        g = d.decompose("Build something")
        assert len(g.nodes) == 5
        g.validate()  # should not raise

    def test_goal_preserved(self):
        d = MockDecomposer()
        g = d.decompose("My goal")
        assert g.goal == "My goal"


# ── WorkerPool ─────────────────────────────────────────────────────

class TestWorkerPool:
    def test_dispatch_and_poll(self):
        backend = MockBackend(min_seconds=0.0, max_seconds=0.01)
        pool = WorkerPool(backend, max_workers=2)
        task = TaskNode(task_id="X", title="X")
        pool.dispatch(task)
        assert pool.active_count() == 1

        import time
        time.sleep(0.05)
        statuses = pool.poll_all()
        assert statuses["X"] == "completed"
        assert pool.active_count() == 0

    def test_can_accept(self):
        backend = MockBackend(min_seconds=10.0, max_seconds=10.0)
        pool = WorkerPool(backend, max_workers=1)
        pool.dispatch(TaskNode(task_id="A", title="A"))
        assert not pool.can_accept()


# ── Tracker ────────────────────────────────────────────────────────

class TestTracker:
    def test_snapshot(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        t = Tracker(g)
        snap = t.snapshot()
        assert snap["goal"] == "test"
        assert "A" in snap["tasks"]

    def test_update(self):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        t = Tracker(g)
        t.update("A", TaskStatus.COMPLETED, "done")
        assert t.snapshot()["tasks"]["A"]["status"] == "completed"

    def test_save_and_load(self, tmp_path):
        g = TaskGraph(goal="test")
        g.add_node(TaskNode(task_id="A", title="A"))
        t = Tracker(g)
        t.update("A", TaskStatus.COMPLETED, "done")
        p = tmp_path / "state.json"
        t.save(p)
        loaded = Tracker.load(p)
        assert loaded["tasks"]["A"]["status"] == "completed"


# ── Orchestrator (end-to-end) ──────────────────────────────────────

class TestOrchestrator:
    def test_full_pipeline(self):
        orch = Orchestrator(
            decomposer=MockDecomposer(),
            worker_backend=MockBackend(min_seconds=0.0, max_seconds=0.01),
            max_workers=4,
            poll_interval=0.01,
        )
        result = orch.run("Build something")
        assert result.status == OrchestrationStatus.COMPLETED
        tasks = result.snapshot["tasks"]
        assert all(t["status"] == "completed" for t in tasks.values())
        assert result.elapsed_seconds > 0
