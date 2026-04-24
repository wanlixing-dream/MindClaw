from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AgentRole(StrEnum):
    LEADER = "leader"
    WORKER = "worker"
    SPECIALIST = "specialist"


class TeamStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


@dataclass(slots=True)
class TeamMember:
    name: str
    agent_id: str
    role: AgentRole = AgentRole.WORKER
    runtime: str = "default"
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Team:
    name: str
    goal: str = ""
    status: TeamStatus = TeamStatus.DRAFT
    members: list[TeamMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)

    def add_member(self, member: TeamMember) -> None:
        if any(existing.name == member.name for existing in self.members):
            raise ValueError(f"Member '{member.name}' already exists in team '{self.name}'.")
        self.members.append(member)

    def get_member(self, name: str) -> TeamMember | None:
        for member in self.members:
            if member.name == name:
                return member
        return None

    def leader(self) -> TeamMember | None:
        for member in self.members:
            if member.role == AgentRole.LEADER:
                return member
        return None
