import pytest

from core.event_bus import EventBus, Event


def test_event_bus_subscribe_and_publish():
    bus = EventBus()
    received = []

    def handler(event: Event):
        received.append(event)

    bus.subscribe("test_topic", handler)
    bus.publish("test_topic", {"key": "value"})

    assert len(received) == 1
    assert received[0].topic == "test_topic"
    assert received[0].payload == {"key": "value"}


def test_publish_propagates_handler_exception():
    bus = EventBus()

    def handler(event: Event) -> None:
        raise ValueError("boom")

    bus.subscribe("fail", handler)

    with pytest.raises(ValueError, match="boom"):
        bus.publish("fail")
