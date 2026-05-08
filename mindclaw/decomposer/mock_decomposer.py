from __future__ import annotations

from mindclaw.decomposer.interface import DecomposerBase
from mindclaw.scheduler.graph import TaskGraph, TaskNode


class MockDecomposer(DecomposerBase):
    """Returns a fixed task graph for any goal. Used for MVP testing."""

    def decompose(self, goal: str) -> TaskGraph:
        graph = TaskGraph(goal=goal)

        graph.add_node(TaskNode(
            task_id="T1",
            title="Analyze requirements and design architecture",
            description=f"Understand the goal: '{goal}' and produce a high-level design.",
        ))
        graph.add_node(TaskNode(
            task_id="T2",
            title="Implement core backend logic",
            description="Build the main backend components based on the design.",
            depends_on=["T1"],
        ))
        graph.add_node(TaskNode(
            task_id="T3",
            title="Implement frontend interface",
            description="Build the frontend UI based on the design.",
            depends_on=["T1"],
        ))
        graph.add_node(TaskNode(
            task_id="T4",
            title="Write integration tests",
            description="Write tests that cover the backend and frontend integration.",
            depends_on=["T2", "T3"],
        ))
        graph.add_node(TaskNode(
            task_id="T5",
            title="Final review and documentation",
            description="Review all work, fix issues, and write documentation.",
            depends_on=["T4"],
        ))

        return graph
