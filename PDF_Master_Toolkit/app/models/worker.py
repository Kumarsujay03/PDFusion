"""Background worker for long-running operations."""
import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """Signals for background worker communication."""

    started = Signal()
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)
    progress_detail = Signal(int, str)
    cancelled = Signal()


class Worker(QRunnable):
    """Background worker for executing tasks in a thread pool."""

    def __init__(
        self,
        fn: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_cancelled = False
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        """Execute the worker function."""
        self.signals.started.emit()
        try:
            # Pass progress callback and cancel check to the function
            self.kwargs["progress_callback"] = self.signals.progress.emit
            self.kwargs["progress_detail_callback"] = self.signals.progress_detail.emit
            self.kwargs["is_cancelled"] = self.check_cancelled
            result = self.fn(*self.args, **self.kwargs)
            if not self._is_cancelled:
                self.signals.result.emit(result)
        except Exception as e:
            if not self._is_cancelled:
                tb = traceback.format_exc()
                self.signals.error.emit(f"{str(e)}\n{tb}")
        finally:
            if self._is_cancelled:
                self.signals.cancelled.emit()
            else:
                self.signals.finished.emit()

    def cancel(self) -> None:
        """Request cancellation of the worker."""
        self._is_cancelled = True

    def check_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._is_cancelled
