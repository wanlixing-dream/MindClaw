from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    home_dir: Path

    @property
    def teams_file(self) -> Path:
        return self.home_dir / "teams.json"

    @property
    def tasks_file(self) -> Path:
        return self.home_dir / "tasks.json"


def load_settings() -> Settings:
    configured = os.environ.get("MINDCLAW_HOME")
    home_dir = Path(configured).expanduser() if configured else Path.cwd() / ".mindclaw"
    return Settings(home_dir=home_dir)
