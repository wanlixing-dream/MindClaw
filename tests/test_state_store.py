from pathlib import Path

from mindclaw.config import Settings
from mindclaw.state import JsonStateStore
from mindclaw.task import Task
from mindclaw.team import AgentRole, Team, TeamMember


def test_json_state_store_persists_teams_and_tasks(tmp_path: Path) -> None:
    settings = Settings(home_dir=tmp_path / ".mindclaw")
    store = JsonStateStore(settings)

    team = Team(name="demo", goal="ship mvp")
    team.add_member(TeamMember(name="leader", agent_id="a1", role=AgentRole.LEADER))
    store.save_team(team)

    task = Task(task_id="t1", title="design cli", team_name="demo")
    store.save_task(task)

    loaded_team = store.get_team("demo")
    loaded_tasks = store.list_tasks(team_name="demo")

    assert loaded_team is not None
    assert loaded_team.goal == "ship mvp"
    assert loaded_team.leader() is not None
    assert loaded_team.leader().name == "leader"
    assert len(loaded_tasks) == 1
    assert loaded_tasks[0].task_id == "t1"
    assert loaded_tasks[0].team_name == "demo"
