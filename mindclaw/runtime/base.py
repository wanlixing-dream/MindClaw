from __future__ import annotations

from abc import ABC, abstractmethod

from mindclaw.runtime.models import RuntimeBootstrap, RuntimeCapability, RuntimeLaunchResult, WorkerHandle


class RuntimeAdapter(ABC):
    """Base interface for plugging a concrete worker runtime into MindClaw."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique runtime name used for registration and lookup."""

    @abstractmethod
    def capability(self) -> RuntimeCapability:
        """Describe the runtime features exposed to the shell."""

    @abstractmethod
    def launch(self, bootstrap: RuntimeBootstrap) -> RuntimeLaunchResult:
        """Launch a new worker using normalized bootstrap context."""

    def resume(self, handle: WorkerHandle) -> RuntimeLaunchResult:
        """Resume a previously launched worker if the runtime supports it."""
        return RuntimeLaunchResult(handle=handle, accepted=False, message="Resume is not implemented.")

    def terminate(self, handle: WorkerHandle) -> None:
        """Terminate a running worker if the runtime supports it."""
