import math
import time
from abc import ABC, abstractmethod


class Task:
    @abstractmethod
    def status(self) -> str:
        pass

    @abstractmethod
    def log(self) -> list[str] | None:
        return None

    @abstractmethod
    def has_log(self) -> bool:
        pass

    @abstractmethod
    @staticmethod
    def status_map() -> dict[str, str]:
        pass



class RunningTask:
    def __init__(self, task: Task, *,
                 skip: int = 0,
                 show_log: bool = True,
                 show_spinner: bool = True,
                 poll: int = 1,
                 timeout: float = None,
                 multiple: bool = False):
        self._show_log = show_log and not multiple and task.has_log()
        self._t0 = time.time()
        self._logs = []
        
                 
                 
                 

    

class Task:
    def __init__(self):
        
