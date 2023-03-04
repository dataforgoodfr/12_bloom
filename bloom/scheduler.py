from collections.abc import Callable
from threading import Lock, Timer
from typing import Any


class PeriodicScheduler:
    """A periodic task running in threading.Timers
    From https://stackoverflow.com/a/18906292/14541668.
    """

    def __init__(
        self,
        interval: float,
        function: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Init the scheduler. You have to call start() after initialization.
        ::interval:: interval in seconds to run the function.
        ::function:: function to run.
        ::args:: args to pass to the function.
        ::kwargs:: kwargs to pass to the function.
        """
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True

    def start(self, from_run: bool = False) -> None:
        """Start the scheduler.
        ::from_run:: For internal purposes to allow re-scheduling
        Please do not use from_run=True until you know what you do !.
        """
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
        self._lock.release()

    def _run(self) -> None:
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self) -> None:
        """Stop the scheduler."""
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()
