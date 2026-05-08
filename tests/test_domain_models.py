from mindclaw.decomposer import MockDecomposer
from mindclaw.orchestrator import Orchestrator
from mindclaw.orchestrator.models import OrchestrationStatus
from mindclaw.task import Task, TaskStatus
from mindclaw.team import AgentRole, Team, TeamMember
from mindclaw.worker_pool import MockBackend


def test_team_add_member_and_find_leader() -> None:
    team = Team(name="demo")
    leader = TeamMember(name="leader", agent_id="a1", role=AgentRole.LEADER)
    worker = TeamMember(name="worker", agent_id="a2")

    team.add_member(leader)
    team.add_member(worker)

    assert team.leader() == leader
    assert team.get_member("worker") == worker


def test_task_mark_updates_status() -> None:
    task = Task(task_id="t1", title="Do work")

    task.mark(TaskStatus.IN_PROGRESS)

    assert task.status == TaskStatus.IN_PROGRESS


def test_orchestrator_run_completes() -> None:
    orchestrator = Orchestrator(
        decomposer=MockDecomposer(),
        worker_backend=MockBackend(min_seconds=0.0, max_seconds=0.01),
        max_workers=4,
        poll_interval=0.01,
    )

    result = orchestrator.run("Build something")

    assert result.status == OrchestrationStatus.COMPLETED
