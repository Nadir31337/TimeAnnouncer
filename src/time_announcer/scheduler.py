import threading
from datetime import datetime
from typing import Callable


class Scheduler:
    def __init__(self, interval_seconds: int, on_tick: Callable[[str], None]):
        self.interval_seconds = interval_seconds
        self.on_tick = on_tick
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            current_time = datetime.now().strftime("%I:%M %p")
            self.on_tick(current_time)
            self._stop_event.wait(self.interval_seconds)