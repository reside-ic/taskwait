import math
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass


class Task(ABC):
    status_waiting: set[str]
    status_running: set[str]

    @abstractmethod
    def status(self) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def log(self) -> list[str] | None:
        return None  # pragma: no cover

    @abstractmethod
    def has_log(self) -> bool:
        pass  # pragma: no cover


@dataclass
class Result:
    status: str
    start: float
    end: float


class RunningTask:
    def __init__(
        self,
        task: Task,
        *,
        show_log: bool = True,
        progress: bool = True,
        poll: int = 1,
        timeout: float | None = None,
    ):
        self._task = task
        self._show_log = show_log and task.has_log()
        self._progress = progress and not self._show_log
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
        display = self._show_log or self._progress
        with very_simple_progress("Waiting", display=display) as p:
            while self._status in self._task.status_waiting:
                p()
                self._status = self._task_status()

    def _wait_to_finish(self) -> None:
        with very_simple_progress("Running", display=self._progress) as p:
            while self._status in self._task.status_running:
                p()
                self._show_new_log()
                self._status = self._task_status()
        self._show_new_log()

    def _task_status(self) -> str:
        self._last_time = _delay(self._last_time, self._poll, self._time_end)
        return self._task.status()

    def _show_new_log(self) -> None:
        if self._show_log:
            self._skip = _show_new_log(self._skip, self._task.log())


def taskwait(
    task: Task,
    *,
    show_log: bool = True,
    progress: bool = True,
    poll: int = 1,
    timeout: float | None = None,
) -> Result:
    t = RunningTask(
        task, show_log=show_log, progress=progress, poll=poll, timeout=timeout
    )
    return t.run()


def _delay(prev, poll, end) -> float:
    now = time.time()
    if prev is None:
        return now
    if now > end:
        raise TimeoutError()
    wait = poll - (now - prev)
    if wait > 0:
        time.sleep(wait)
    return now


def _show_new_log(skip: int, value: list[str] | None) -> int:
    if not value or len(value) <= skip:
        return skip
    print("\n".join(value[skip:]))
    return len(value)


# Small stub that we'll swap in for something better later.
@contextmanager
def very_simple_progress(start, end="OK", *, display: bool = True):
    if display:
        print(start, end="", flush=True)

    def fn():
        if display:
            print(".", end="", flush=True)

    try:
        yield fn
    finally:
        if display:
            print(end, flush=True)
