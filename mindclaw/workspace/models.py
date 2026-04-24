from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkspaceMode(StrEnum):
    SHARED = "shared"
    ISOLATED = "isolated"


class WorkspaceStatus(StrEnum):
    READY = "ready"
    DIRTY = "dirty"
    MERGED = "merged"
    REMOVED = "removed"


@dataclass(slots=True)
class WorkspaceRef:
    root_path: str
    branch_name: str = ""
    mode: WorkspaceMode = WorkspaceMode.ISOLATED


@dataclass(slots=True)
class WorkspaceAssignment:
    team_name: str
    agent_name: str
    workspace: WorkspaceRef
    status: WorkspaceStatus = WorkspaceStatus.READY
    created_at: datetime = field(default_factory=utc_now)
