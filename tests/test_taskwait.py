import math
import time
from unittest import mock

import pytest

from taskwait import Result, Task, _delay, _show_new_log, taskwait


class ExampleTask(Task):
    def __init__(self, plan, *, show_logs: bool = False):
        self.plan = list(reversed(plan))
        self.n = 0
        self.show_logs = show_logs
        self.status_waiting = {"created", "submitted"}
        self.status_running = {"running", "finishing"}
        self.logs: list[str] = []

    def status(self):
        return self.plan.pop()

    def log(self) -> list[str]:
        self.logs.append(f"Log entry {len(self.logs) + 1}")
        return self.logs

    def has_log(self) -> bool:
        return self.show_logs


def test_can_wait_for_task():
    task = ExampleTask(["created", "submitted", "running", "finishing", "done"])
    result = taskwait(task, poll=0)
    assert isinstance(result, Result)
    assert result.status == "done"


def test_can_print_logs(capsys):
    task = ExampleTask(
        ["created", "submitted", "running", "finishing", "done"], show_logs=True
    )
    result = taskwait(task, poll=0)
    assert result.status == "done"
    out = capsys.readouterr().out
    assert out == (
        "Waiting..OK\n" + "".join([f"Log entry {i + 1}\n" for i in range(3)])
    )


def test_can_timeout():
    prev = time.time() - 100
    end = time.time() - 1
    with pytest.raises(TimeoutError):
        _delay(prev, 0, end)


def test_delay_if_required(mocker):
    t = 1000000
    poll = 10
    end = math.inf
    mock_sleep = mock.MagicMock()
    mock_time = mock.MagicMock(return_value=t)
    mocker.patch("time.time", mock_time)
    mocker.patch("time.sleep", mock_sleep)

    # We don't call sleep if we've never called the function before:
    assert _delay(None, poll, end) == t
    assert mock_time.call_count == 1
    assert mock_sleep.call_count == 0

    # We don't call sleep if we waited more than poll seconds since last time
    assert _delay(t - 20, poll, end) == t
    assert mock_time.call_count == 2
    assert mock_sleep.call_count == 0

    # We don't call sleep if we waited more than poll seconds since last time
    assert _delay(t - 3, poll, end) == t
    assert mock_time.call_count == 3
    assert mock_sleep.call_count == 1
    assert mock_sleep.mock_calls[0] == mock.call(7)


def test_can_tail_logs(capsys):
    assert _show_new_log(0, None) == 0
    assert _show_new_log(0, []) == 0
    assert _show_new_log(3, ["a", "b", "c"]) == 3
    assert capsys.readouterr().out == ""
    assert _show_new_log(1, ["a", "b", "c"]) == 3
    assert capsys.readouterr().out == "b\nc\n"
