from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    topic: str
    payload: Any = None


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, topic: str, handler: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    def publish(self, topic: str, payload: Any = None) -> None:
        for handler in self._subscribers.get(topic, []):
            try:
                handler(Event(topic=topic, payload=payload))
            except Exception:
                pass
