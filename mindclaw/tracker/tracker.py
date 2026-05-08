from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from mindclaw.scheduler.graph import TaskGraph, TaskStatus


class Tracker:
    """Tracks global task state and provides progress summaries."""

    def __init__(self, graph: TaskGraph) -> None:
        self._graph = graph
        self._results: dict[str, str] = {}
        self._started_at = datetime.now(timezone.utc)

    def update(self, task_id: str, status: TaskStatus, result: str = "") -> None:
        node = self._graph.nodes.get(task_id)
        if node is None:
            return
        node.status = status
        if result:
            node.result = result
            self._results[task_id] = result

    def snapshot(self) -> dict:
        return {
            "goal": self._graph.goal,
            "started_at": self._started_at.isoformat(),
            "tasks": {
                tid: {
                    "title": n.title,
                    "status": n.status.value,
                    "assigned_to": n.assigned_to,
                    "depends_on": n.depends_on,
                    "result": n.result,
                }
                for tid, n in self._graph.nodes.items()
            },
        }

    def summary(self) -> str:
        status_icons = {
            TaskStatus.PENDING: "\u23f3",   # ⏳
            TaskStatus.READY: "\u23f3",     # ⏳
            TaskStatus.RUNNING: "\U0001f504",  # 🔄
            TaskStatus.COMPLETED: "\u2705",    # ✅
            TaskStatus.FAILED: "\u274c",       # ❌
        }
        lines = [f"\n\U0001f680 Goal: {self._graph.goal}\n"]
        for tid, node in self._graph.nodes.items():
            icon = status_icons.get(node.status, "?")
            worker = f" [{node.assigned_to}]" if node.assigned_to else ""
            lines.append(f"  {icon} {tid}: {node.title}{worker}")

        completed = sum(1 for n in self._graph.nodes.values() if n.status == TaskStatus.COMPLETED)
        total = len(self._graph.nodes)
        lines.append(f"\n  Progress: {completed}/{total} tasks completed")
        return "\n".join(lines)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.snapshot(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))
