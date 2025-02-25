import math
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


class Task(ABC):
    status_waiting: list[str]
    status_running: list[str]

    @abstractmethod
    def status(self) -> str:
        pass

    @abstractmethod
    def log(self) -> list[str] | None:
        return None

    @abstractmethod
    def has_log(self) -> bool:
        pass


@dataclass
class Result:
    status: str
    start: float
    end: float


# not yet supported: spinner (and progress in general), multiple tasks
class RunningTask:
    def __init__(
        self,
        task: Task,
        *,
        show_log: bool = True,
        poll: int = 1,
        timeout: float | None = None,
    ):
        self._task = task
        self._show_log = show_log and task.has_log()
        self._poll = poll
        self._skip = 0
        self._t0 = time.time()
        self._status = self._task.status()
        self._last_time: float | None = None
        self._time_end = math.inf if timeout is None else time.time() + timeout

    def run(self) -> Result:
        self._wait_to_start()
        self._wait_to_finish()
        return Result(self._status, self._t0, time.time())

    def _wait_to_start(self) -> None:
        while self._status in self._task.status_waiting:
            self._status = self._task.status()

    def _wait_to_finish(self) -> None:
        while self._status in self._task.status_running:
            self._show_new_log()
            self._status = self._task.status()
        self._show_new_log()

    def _task_status(self) -> str:
        if self._last_time is not None:
            now = time.time()
            if now > self._time_end:
                raise TimeoutError()
            wait = self._poll - (now - self._last_time)
            if wait > 0:
                time.sleep(wait)
        self._last_time = time.time()
        return self._task.status()

    def _show_new_log(self) -> None:
        if self._show_log:
            curr = self._task.log()
            if curr and len(curr) > self._skip:
                print("\n".join(curr[self._skip :]))
                self._skip = len(curr)


def taskwait(
    task: Task,
    *,
    show_log: bool = True,
    poll: int = 1,
    timeout: float | None = None,
) -> Result:
    t = RunningTask(task, show_log=show_log, poll=poll, timeout=timeout)
    return t.run()
