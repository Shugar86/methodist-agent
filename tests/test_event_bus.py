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
