from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrchestrationStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OrchestrationResult:
    goal: str
    status: OrchestrationStatus
    snapshot: dict
    elapsed_seconds: float = 0.0

    @property
    def summary(self) -> str:
        tasks = self.snapshot.get("tasks", {})
        completed = sum(1 for t in tasks.values() if t["status"] == "completed")
        failed = sum(1 for t in tasks.values() if t["status"] == "failed")
        total = len(tasks)
        lines = [
            f"\n{'=' * 50}",
            f"Goal: {self.goal}",
            f"Status: {self.status.value}",
            f"Tasks: {completed}/{total} completed, {failed} failed",
            f"Time: {self.elapsed_seconds:.1f}s",
            f"{'=' * 50}",
        ]
        return "\n".join(lines)
