from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from mindclaw.task.models import Task


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrchestrationStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class OrchestrationPlan:
    team_name: str
    goal: str
    phases: list[str] = field(default_factory=lambda: ["plan", "execute", "verify"])
    tasks: list[Task] = field(default_factory=list)


@dataclass(slots=True)
class OrchestrationState:
    team_name: str
    current_phase: str = "plan"
    status: OrchestrationStatus = OrchestrationStatus.DRAFT
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def advance(self, next_phase: str) -> None:
        self.current_phase = next_phase
        self.updated_at = utc_now()
