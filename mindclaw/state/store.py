from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from mindclaw.config import Settings, load_settings
from mindclaw.task import Task, TaskPriority, TaskStatus
from mindclaw.team import AgentRole, Team, TeamMember, TeamStatus


class JsonStateStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()

    def ensure(self) -> None:
        self.settings.home_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_file(self.settings.teams_file)
        self._ensure_file(self.settings.tasks_file)

    def list_teams(self) -> list[Team]:
        records = self._read_json(self.settings.teams_file)
        return [self._team_from_record(record) for record in records]

    def get_team(self, name: str) -> Team | None:
        for team in self.list_teams():
            if team.name == name:
                return team
        return None

    def save_team(self, team: Team) -> None:
        teams = self.list_teams()
        for existing in teams:
            if existing.name == team.name:
                raise ValueError(f"Team '{team.name}' already exists.")
        teams.append(team)
        self._write_json(self.settings.teams_file, [self._team_to_record(item) for item in teams])

    def list_tasks(self, team_name: str | None = None) -> list[Task]:
        records = self._read_json(self.settings.tasks_file)
        tasks = [self._task_from_record(record) for record in records]
        if team_name is None:
            return tasks
        return [task for task in tasks if task.team_name == team_name]

    def save_task(self, task: Task) -> None:
        tasks = self.list_tasks()
        for existing in tasks:
            if existing.task_id == task.task_id and existing.team_name == task.team_name:
                raise ValueError(
                    f"Task '{task.task_id}' already exists in team '{task.team_name}'."
                )
        tasks.append(task)
        self._write_json(self.settings.tasks_file, [self._task_to_record(item) for item in tasks])

    def _ensure_file(self, path: Path) -> None:
        if not path.exists():
            path.write_text("[]\n", encoding="utf-8")

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        self.ensure()
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return []
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError(f"State file '{path}' does not contain a JSON list.")
        return data

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        self.ensure()
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _team_to_record(self, team: Team) -> dict[str, Any]:
        return {
            "name": team.name,
            "goal": team.goal,
            "status": team.status.value,
            "members": [
                {
                    "name": member.name,
                    "agent_id": member.agent_id,
                    "role": member.role.value,
                    "runtime": member.runtime,
                    "metadata": dict(member.metadata),
                }
                for member in team.members
            ],
            "created_at": team.created_at.isoformat(),
        }

    def _team_from_record(self, record: dict[str, Any]) -> Team:
        return Team(
            name=record["name"],
            goal=record.get("goal", ""),
            status=TeamStatus(record.get("status", TeamStatus.DRAFT.value)),
            members=[
                TeamMember(
                    name=member["name"],
                    agent_id=member["agent_id"],
                    role=AgentRole(member.get("role", AgentRole.WORKER.value)),
                    runtime=member.get("runtime", "default"),
                    metadata=member.get("metadata", {}),
                )
                for member in record.get("members", [])
            ],
            created_at=datetime.fromisoformat(record["created_at"]),
        )

    def _task_to_record(self, task: Task) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "team_name": task.team_name,
            "title": task.title,
            "description": task.description,
            "owner": task.owner,
            "status": task.status.value,
            "priority": task.priority.value,
            "blocked_by": list(task.blocked_by),
            "metadata": dict(task.metadata),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    def _task_from_record(self, record: dict[str, Any]) -> Task:
        return Task(
            task_id=record["task_id"],
            team_name=record.get("team_name", ""),
            title=record["title"],
            description=record.get("description", ""),
            owner=record.get("owner", ""),
            status=TaskStatus(record.get("status", TaskStatus.PENDING.value)),
            priority=TaskPriority(record.get("priority", TaskPriority.MEDIUM.value)),
            blocked_by=record.get("blocked_by", []),
            metadata=record.get("metadata", {}),
            created_at=datetime.fromisoformat(record["created_at"]),
            updated_at=datetime.fromisoformat(record["updated_at"]),
        )
