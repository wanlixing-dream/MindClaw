from mindclaw.orchestrator import Orchestrator
from mindclaw.runtime.registry import RuntimeRegistry
from mindclaw.task import Task, TaskStatus
from mindclaw.team import AgentRole, Team, TeamMember


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


def test_orchestrator_start_creates_running_state() -> None:
    team = Team(name="demo")
    orchestrator = Orchestrator(RuntimeRegistry())

    state = orchestrator.start(team)

    assert state.team_name == "demo"
    assert state.current_phase == "plan"
    assert state.status == "running"
