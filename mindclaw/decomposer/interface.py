from __future__ import annotations

from abc import ABC, abstractmethod

from mindclaw.scheduler.graph import TaskGraph


class DecomposerBase(ABC):
    """Abstract interface for task decomposition strategies."""

    @abstractmethod
    def decompose(self, goal: str) -> TaskGraph:
        """Break a high-level goal into a TaskGraph with dependencies."""
