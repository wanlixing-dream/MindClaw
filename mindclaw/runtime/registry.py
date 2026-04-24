from __future__ import annotations

from mindclaw.runtime.base import RuntimeAdapter


class RuntimeRegistry:
    """In-memory registry for runtime adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, RuntimeAdapter] = {}

    def register(self, adapter: RuntimeAdapter) -> None:
        if adapter.name in self._adapters:
            raise ValueError(f"Runtime '{adapter.name}' is already registered.")
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> RuntimeAdapter:
        try:
            return self._adapters[name]
        except KeyError as exc:
            raise KeyError(f"Runtime '{name}' is not registered.") from exc

    def list_names(self) -> list[str]:
        return sorted(self._adapters.keys())
