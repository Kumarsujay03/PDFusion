"""Batch processing queue manager widget."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from PySide6.QtCore import Qt, Signal, QThreadPool
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
)

from app.models.worker import Worker


class JobStatus(Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class BatchJob:
    """Represents a batch processing job."""

    id: int
    name: str
    operation: Callable
    kwargs: dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class BatchQueueWidget(QWidget):
    """Widget for managing batch processing jobs."""

    job_completed = Signal(int)  # job_id
    all_completed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._jobs: list[BatchJob] = []
        self._job_counter = 0
        self._current_worker: Optional[Worker] = None
        self._is_running = False
        self._thread_pool = QThreadPool.globalInstance()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title = QLabel("Batch Queue")
        title.setObjectName("section_title")
        header.addWidget(title)

        self._status_label = QLabel("Idle")
        self._status_label.setStyleSheet("color: #6c7086; font-size: 9pt;")
        header.addWidget(self._status_label)
        header.addStretch()

        self._start_btn = QPushButton("▶ Start")
        self._start_btn.setObjectName("secondary")
        self._start_btn.setFixedHeight(30)
        self._start_btn.clicked.connect(self.start_queue)
        header.addWidget(self._start_btn)

        self._stop_btn = QPushButton("⏹ Stop")
        self._stop_btn.setObjectName("danger")
        self._stop_btn.setFixedHeight(30)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self.stop_queue)
        header.addWidget(self._stop_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("secondary")
        self._clear_btn.setFixedHeight(30)
        self._clear_btn.clicked.connect(self.clear_completed)
        header.addWidget(self._clear_btn)

        layout.addLayout(header)

        # Progress
        self._overall_progress = QProgressBar()
        self._overall_progress.setFixedHeight(8)
        self._overall_progress.setTextVisible(False)
        layout.addWidget(self._overall_progress)

        # Job list
        self._job_list = QListWidget()
        layout.addWidget(self._job_list)

    def add_job(
        self,
        name: str,
        operation: Callable,
        **kwargs: Any,
    ) -> int:
        """Add a job to the queue. Returns job ID."""
        self._job_counter += 1
        job = BatchJob(
            id=self._job_counter,
            name=name,
            operation=operation,
            kwargs=kwargs,
        )
        self._jobs.append(job)
        self._update_list()
        return job.id

    def start_queue(self) -> None:
        """Start processing the queue."""
        if self._is_running:
            return

        self._is_running = True
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText("Processing...")
        self._process_next()

    def stop_queue(self) -> None:
        """Stop processing the queue."""
        self._is_running = False
        if self._current_worker:
            self._current_worker.cancel()
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("Stopped")

    def clear_completed(self) -> None:
        """Remove completed and failed jobs from the list."""
        self._jobs = [
            j for j in self._jobs
            if j.status in (JobStatus.QUEUED, JobStatus.RUNNING)
        ]
        self._update_list()

    def _process_next(self) -> None:
        """Process the next queued job."""
        if not self._is_running:
            return

        # Find next queued job
        next_job = None
        for job in self._jobs:
            if job.status == JobStatus.QUEUED:
                next_job = job
                break

        if not next_job:
            self._is_running = False
            self._start_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._status_label.setText("All jobs completed")
            self.all_completed.emit()
            return

        next_job.status = JobStatus.RUNNING
        self._update_list()

        worker = Worker(next_job.operation, **next_job.kwargs)
        worker.signals.progress.connect(
            lambda p, job=next_job: self._on_job_progress(job, p)
        )
        worker.signals.finished.connect(
            lambda job=next_job: self._on_job_finished(job)
        )
        worker.signals.error.connect(
            lambda e, job=next_job: self._on_job_error(job, e)
        )

        self._current_worker = worker
        self._thread_pool.start(worker)

    def _on_job_progress(self, job: BatchJob, progress: int) -> None:
        job.progress = progress
        self._update_overall_progress()
        self._update_list()

    def _on_job_finished(self, job: BatchJob) -> None:
        job.status = JobStatus.COMPLETED
        job.progress = 100
        self._update_list()
        self.job_completed.emit(job.id)
        self._process_next()

    def _on_job_error(self, job: BatchJob, error: str) -> None:
        job.status = JobStatus.FAILED
        job.error = error.split("\n")[0]
        self._update_list()
        self._process_next()

    def _update_list(self) -> None:
        """Update the job list display."""
        self._job_list.clear()
        for job in self._jobs:
            status_icons = {
                JobStatus.QUEUED: "⏳",
                JobStatus.RUNNING: "⚙️",
                JobStatus.COMPLETED: "✅",
                JobStatus.FAILED: "❌",
                JobStatus.CANCELLED: "🚫",
            }
            icon = status_icons.get(job.status, "")
            text = f"{icon} {job.name} [{job.status.value}]"
            if job.status == JobStatus.RUNNING:
                text += f" ({job.progress}%)"
            elif job.status == JobStatus.FAILED:
                text += f" - {job.error[:50]}"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, job.id)
            self._job_list.addItem(item)

        self._update_overall_progress()

    def _update_overall_progress(self) -> None:
        """Update overall progress bar."""
        if not self._jobs:
            self._overall_progress.setValue(0)
            return

        total = len(self._jobs)
        completed = sum(
            1 for j in self._jobs
            if j.status in (JobStatus.COMPLETED, JobStatus.FAILED)
        )
        running_progress = sum(
            j.progress for j in self._jobs if j.status == JobStatus.RUNNING
        ) / 100.0

        overall = int(((completed + running_progress) / total) * 100)
        self._overall_progress.setValue(overall)

    @property
    def pending_count(self) -> int:
        return sum(1 for j in self._jobs if j.status == JobStatus.QUEUED)

    @property
    def is_running(self) -> bool:
        return self._is_running
