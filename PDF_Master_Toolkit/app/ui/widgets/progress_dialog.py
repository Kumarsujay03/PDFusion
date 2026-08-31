"""Progress dialog for long-running operations."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
)


class ProgressDialog(QDialog):
    """Modal progress dialog with cancel support."""

    def __init__(
        self,
        parent=None,
        title: str = "Processing",
        message: str = "Please wait...",
        cancelable: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(450, 180)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )
        self._cancelled = False

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
        layout.addWidget(self._title_label)

        self._message_label = QLabel(message)
        self._message_label.setStyleSheet("font-size: 10pt;")
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        layout.addWidget(self._progress_bar)

        if cancelable:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            self._cancel_btn = QPushButton("Cancel")
            self._cancel_btn.setObjectName("danger")
            self._cancel_btn.setFixedWidth(100)
            self._cancel_btn.clicked.connect(self._on_cancel)
            btn_layout.addWidget(self._cancel_btn)
            layout.addLayout(btn_layout)

    def set_progress(self, value: int) -> None:
        """Set progress bar value (0-100)."""
        self._progress_bar.setValue(value)

    def set_message(self, message: str) -> None:
        """Update the message text."""
        self._message_label.setText(message)

    def set_indeterminate(self, indeterminate: bool = True) -> None:
        """Set progress bar to indeterminate mode."""
        if indeterminate:
            self._progress_bar.setRange(0, 0)
        else:
            self._progress_bar.setRange(0, 100)

    def _on_cancel(self) -> None:
        self._cancelled = True
        self._message_label.setText("Cancelling...")
        if hasattr(self, "_cancel_btn"):
            self._cancel_btn.setEnabled(False)

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled
