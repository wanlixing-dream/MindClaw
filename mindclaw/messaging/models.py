from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MessageType(StrEnum):
    DIRECT = "direct"
    BROADCAST = "broadcast"
    STATUS = "status"
    EVENT = "event"


@dataclass(slots=True)
class Message:
    message_id: str
    sender: str
    recipient: str
    content: str
    type: MessageType = MessageType.DIRECT
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
