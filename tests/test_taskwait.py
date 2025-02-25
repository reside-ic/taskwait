from taskwait import Result, Task, taskwait


class ExampleTask(Task):
    def __init__(self, plan, *, show_logs: bool = False):
        self.plan = list(reversed(plan))
        self.n = 0
        self.show_logs = show_logs
        self.status_waiting = ["created", "submitted"]
        self.status_running = ["running", "finishing"]

    def status(self):
        return self.plan.pop()

    def log(self) -> None:
        self.n += 1
        print(f"Log entry {self.n}")

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
    assert out == "".join([f"Log entry {i + 1}\n" for i in range(3)])
