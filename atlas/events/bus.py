from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum


class EventPriority(IntEnum):
    LOW = 10
    NORMAL = 20
    HIGH = 30
    CRITICAL = 40


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    event_type: str
    source: str
    payload: dict[str, object] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    tags: tuple[str, ...] = ()
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class EventSubscription:
    subscriber_id: str
    event_types: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    min_priority: EventPriority = EventPriority.LOW

    def matches(self, event: EventRecord) -> bool:
        if event.priority < self.min_priority:
            return False
        if self.event_types and event.event_type not in self.event_types:
            return False
        if self.tags and not set(self.tags).intersection(event.tags):
            return False
        return True


class EventBus:
    def __init__(self) -> None:
        self._events: list[EventRecord] = []
        self._subscriptions: dict[str, EventSubscription] = {}

    def publish(self, event: EventRecord) -> None:
        self._events.append(event)

    def subscribe(self, subscription: EventSubscription) -> None:
        self._subscriptions[subscription.subscriber_id] = subscription

    def events_for(self, subscriber_id: str) -> tuple[EventRecord, ...]:
        sub = self._subscriptions[subscriber_id]
        return tuple(e for e in self._events if sub.matches(e))

    def recent(self, limit: int = 100) -> tuple[EventRecord, ...]:
        return tuple(self._events[-limit:])
