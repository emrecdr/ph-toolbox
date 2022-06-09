import pytest

from src.ph_toolbox.event import Event, EventError, EventTypeLog


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    Event.delete()


def test_events():
    n_handler_inputs = {
        "debug": [],
        "info": [],
        "warning": [],
        "error": [],
        "critical": [],
    }

    def _fake_handler(event_type: str, msg: str):
        nonlocal n_handler_inputs
        n_handler_inputs[event_type].append(msg)

    def _fake_debug_handler(msg: str):
        _fake_handler("debug", msg)

    def _fake_info_handler(msg: str):
        _fake_handler("info", msg)

    def _fake_warning_handler(msg: str):
        _fake_handler("warning", msg)

    def _fake_error_handler(msg: str):
        _fake_handler("error", msg)

    def _fake_critical_handler(msg: str):
        _fake_handler("critical", msg)

    Event(EventTypeLog.DEBUG).register("key1", _fake_debug_handler)
    Event(EventTypeLog.INFO).register("key1", _fake_info_handler)
    Event(EventTypeLog.WARNING).register("key1", _fake_warning_handler)
    Event(EventTypeLog.ERROR).register("key1", _fake_error_handler)
    Event(EventTypeLog.CRITICAL).register("key1", _fake_critical_handler)

    Event.set_threshold(EventTypeLog.DEBUG)

    Event(EventTypeLog.DEBUG).fire("Debug message #1")
    Event(EventTypeLog.DEBUG).fire("Debug message #2")
    Event(EventTypeLog.DEBUG).fire("Debug message #3")

    assert len(n_handler_inputs["debug"]) == 3
    assert n_handler_inputs["debug"] == ["Debug message #1", "Debug message #2", "Debug message #3"]

    assert len(n_handler_inputs["info"]) == 0
    assert len(n_handler_inputs["warning"]) == 0
    assert len(n_handler_inputs["error"]) == 0
    assert len(n_handler_inputs["critical"]) == 0

    Event(EventTypeLog.WARNING).fire("Warning is served!")
    Event(EventTypeLog.ERROR).fire("This is an error!")

    assert len(n_handler_inputs["debug"]) == 3
    assert len(n_handler_inputs["info"]) == 0
    assert len(n_handler_inputs["warning"]) == 1
    assert len(n_handler_inputs["error"]) == 1
    assert len(n_handler_inputs["critical"]) == 0

    # test threshold
    n_handler_inputs["debug"] = []
    Event.set_threshold(EventTypeLog.WARNING)
    Event(EventTypeLog.DEBUG).fire("Debug message #1")
    assert len(n_handler_inputs["debug"]) == 0


def test_multiple_event_handler():
    handler_inputs = []

    def _fake_handler(msg: str):
        nonlocal handler_inputs
        handler_inputs.append(msg)

    def _fake_debug_handler_1(msg: str):
        _fake_handler(f"1: {msg}")

    def _fake_debug_handler_2(msg: str):
        _fake_handler(f"2: {msg}")

    def _fake_debug_handler_3(msg: str):
        _fake_handler(f"3: {msg}")

    Event(EventTypeLog.DEBUG).register_all(
        ("key1", _fake_debug_handler_1), ("key2", _fake_debug_handler_2), ("key3", _fake_debug_handler_3)
    )

    Event(EventTypeLog.DEBUG).fire("Debug message #1")
    assert len(handler_inputs) == 3
    assert handler_inputs == ["1: Debug message #1", "2: Debug message #1", "3: Debug message #1"]

    Event(EventTypeLog.DEBUG).fire("Debug message #2")
    Event(EventTypeLog.DEBUG).fire("Debug message #3")

    assert len(handler_inputs) == 9

    handler_inputs = []

    Event(EventTypeLog.DEBUG).unregister("key3")
    Event(EventTypeLog.DEBUG).unregister("key10")
    Event(EventTypeLog.DEBUG).fire("Debug message #1")
    assert len(handler_inputs) == 2
    assert handler_inputs == ["1: Debug message #1", "2: Debug message #1"]


def test_failing_event_handler(capfd):
    n_handler_called = 0

    def _fake_handler(msg: str):
        nonlocal n_handler_called
        n_handler_called += 1
        raise Exception("Sorry!")

    Event(EventTypeLog.DEBUG).register("key", _fake_handler)
    Event(EventTypeLog.DEBUG).fire("Debug message")
    assert n_handler_called == 1
    out, err = capfd.readouterr()
    assert out.strip() == ""
    assert err.strip() == "Event Error: DEBUG unable to run _fake_handler - Exception: Sorry!"


def test_firing_event_handler_before_registering():
    n_handler_called = 0

    def _fake_handler(msg: str):
        nonlocal n_handler_called
        n_handler_called += 1

    with pytest.raises(EventError):
        Event(EventTypeLog.DEBUG).fire("Debug message")


def test_name_of_event():
    assert str(Event(EventTypeLog.DEBUG)) == "Event.EventTypeLog.DEBUG"
