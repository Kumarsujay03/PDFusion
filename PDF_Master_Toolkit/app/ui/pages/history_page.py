"""History page - shows operation history and batch queue."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QMessageBox,
)

from app.models.history import HistoryManager
from app.ui.widgets.batch_queue import BatchQueueWidget


class HistoryPage(QWidget):
    """Page showing operation history and batch queue manager."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._history = HistoryManager()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("History & Batch Processing")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("View operation history and manage batch processing queue.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        tabs = QTabWidget()

        # History tab
        history_widget = self._create_history_tab()
        tabs.addTab(history_widget, "📋 History")

        # Batch queue tab
        self._batch_queue = BatchQueueWidget()
        tabs.addTab(self._batch_queue, "⚙️ Batch Queue")

        layout.addWidget(tabs)

    def _create_history_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # Actions
        actions = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self._refresh_history)
        actions.addWidget(refresh_btn)

        actions.addStretch()

        clear_btn = QPushButton("Clear History")
        clear_btn.setObjectName("danger")
        clear_btn.clicked.connect(self._clear_history)
        actions.addWidget(clear_btn)

        layout.addLayout(actions)

        # Table
        self._history_table = QTableWidget()
        self._history_table.setColumnCount(6)
        self._history_table.setHorizontalHeaderLabels([
            "Time", "Operation", "Description", "Input", "Status", "Duration"
        ])
        self._history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._history_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._history_table.setAlternatingRowColors(True)
        self._history_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self._history_table)

        self._refresh_history()
        return widget

    def _refresh_history(self) -> None:
        """Refresh the history table."""
        records = self._history.get_records(limit=100)
        self._history_table.setRowCount(len(records))

        for row, record in enumerate(records):
            # Time
            time_str = record.timestamp[:19].replace("T", " ")
            self._history_table.setItem(row, 0, QTableWidgetItem(time_str))

            # Operation
            self._history_table.setItem(row, 1, QTableWidgetItem(record.operation_type))

            # Description
            self._history_table.setItem(row, 2, QTableWidgetItem(record.description))

            # Input files
            input_str = ", ".join(
                [f.split("\\")[-1].split("/")[-1] for f in record.input_files[:3]]
            )
            if len(record.input_files) > 3:
                input_str += f" (+{len(record.input_files) - 3} more)"
            self._history_table.setItem(row, 3, QTableWidgetItem(input_str))

            # Status
            status = "✅ Success" if record.success else f"❌ {record.error_message[:30]}"
            self._history_table.setItem(row, 4, QTableWidgetItem(status))

            # Duration
            duration = f"{record.duration_seconds:.1f}s" if record.duration_seconds > 0 else "-"
            self._history_table.setItem(row, 5, QTableWidgetItem(duration))

    def _clear_history(self) -> None:
        """Clear all history."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all operation history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._history.clear()
            self._refresh_history()

    @property
    def batch_queue(self) -> BatchQueueWidget:
        return self._batch_queue
