from __future__ import annotations

from mindclaw.orchestrator.models import OrchestrationPlan, OrchestrationState, OrchestrationStatus
from mindclaw.runtime.registry import RuntimeRegistry
from mindclaw.team.models import Team


class Orchestrator:
    """Minimal orchestration service coordinating shell-level state."""

    def __init__(self, runtime_registry: RuntimeRegistry | None = None) -> None:
        self.runtime_registry = runtime_registry or RuntimeRegistry()

    def create_plan(self, team: Team, goal: str) -> OrchestrationPlan:
        return OrchestrationPlan(team_name=team.name, goal=goal)

    def start(self, team: Team) -> OrchestrationState:
        return OrchestrationState(
            team_name=team.name,
            status=OrchestrationStatus.RUNNING,
            current_phase="plan",
        )
