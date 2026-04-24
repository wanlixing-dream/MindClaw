from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class RuntimeBootstrap:
    team_name: str
    agent_name: str
    agent_id: str
    role: str
    task_summary: str = ""
    system_prompt: str = ""
    workspace_path: str = ""
    environment: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class RuntimeCapability:
    supports_tools: bool = True
    supports_memory: bool = False
    supports_sessions: bool = False
    supports_delegation: bool = False


@dataclass(slots=True)
class WorkerHandle:
    runtime_name: str
    worker_id: str
    session_id: str = ""
    process_ref: str = ""
    launched_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class RuntimeLaunchResult:
    handle: WorkerHandle
    accepted: bool = True
    message: str = ""
