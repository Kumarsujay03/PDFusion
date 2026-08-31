"""File list widget for managing input files."""
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
)


class FileListWidget(QWidget):
    """Widget for displaying and managing a list of files."""

    files_changed = Signal(list)

    def __init__(self, parent=None, title: str = "Selected Files") -> None:
        super().__init__(parent)
        self._files: list[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("section_title")
        header.addWidget(title_label)

        self._count_label = QLabel("0 files")
        self._count_label.setStyleSheet("color: #6c7086; font-size: 9pt;")
        header.addWidget(self._count_label)
        header.addStretch()

        # Action buttons
        self._clear_btn = QPushButton("Clear All")
        self._clear_btn.setObjectName("secondary")
        self._clear_btn.setFixedHeight(30)
        self._clear_btn.clicked.connect(self.clear_files)
        header.addWidget(self._clear_btn)

        layout.addLayout(header)

        # List
        self._list_widget = QListWidget()
        self._list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._list_widget.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        self._list_widget.model().rowsMoved.connect(self._on_reorder)
        layout.addWidget(self._list_widget)

        # Bottom actions
        bottom_actions = QHBoxLayout()
        self._remove_btn = QPushButton("Remove Selected")
        self._remove_btn.setObjectName("secondary")
        self._remove_btn.setFixedHeight(30)
        self._remove_btn.clicked.connect(self._remove_selected)
        bottom_actions.addWidget(self._remove_btn)

        self._move_up_btn = QPushButton("▲ Up")
        self._move_up_btn.setObjectName("secondary")
        self._move_up_btn.setFixedHeight(30)
        self._move_up_btn.clicked.connect(self._move_up)
        bottom_actions.addWidget(self._move_up_btn)

        self._move_down_btn = QPushButton("▼ Down")
        self._move_down_btn.setObjectName("secondary")
        self._move_down_btn.setFixedHeight(30)
        self._move_down_btn.clicked.connect(self._move_down)
        bottom_actions.addWidget(self._move_down_btn)

        bottom_actions.addStretch()
        layout.addLayout(bottom_actions)

    def add_files(self, files: list[str]) -> None:
        """Add files to the list."""
        for file_path in files:
            if file_path not in self._files:
                self._files.append(file_path)
                item = QListWidgetItem(Path(file_path).name)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                item.setToolTip(file_path)
                self._list_widget.addItem(item)
        self._update_count()
        self.files_changed.emit(self._files)

    def clear_files(self) -> None:
        """Clear all files."""
        self._files.clear()
        self._list_widget.clear()
        self._update_count()
        self.files_changed.emit(self._files)

    def get_files(self) -> list[str]:
        """Get the current list of files in order."""
        files = []
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            files.append(item.data(Qt.ItemDataRole.UserRole))
        return files

    def _remove_selected(self) -> None:
        """Remove selected files."""
        for item in self._list_widget.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in self._files:
                self._files.remove(path)
            self._list_widget.takeItem(self._list_widget.row(item))
        self._update_count()
        self.files_changed.emit(self._files)

    def _move_up(self) -> None:
        """Move selected item up."""
        row = self._list_widget.currentRow()
        if row > 0:
            item = self._list_widget.takeItem(row)
            self._list_widget.insertItem(row - 1, item)
            self._list_widget.setCurrentRow(row - 1)
            self._files = self.get_files()
            self.files_changed.emit(self._files)

    def _move_down(self) -> None:
        """Move selected item down."""
        row = self._list_widget.currentRow()
        if row < self._list_widget.count() - 1:
            item = self._list_widget.takeItem(row)
            self._list_widget.insertItem(row + 1, item)
            self._list_widget.setCurrentRow(row + 1)
            self._files = self.get_files()
            self.files_changed.emit(self._files)

    def _on_reorder(self) -> None:
        """Handle drag-drop reorder."""
        self._files = self.get_files()
        self.files_changed.emit(self._files)

    def _update_count(self) -> None:
        """Update file count label."""
        count = len(self._files)
        self._count_label.setText(f"{count} file{'s' if count != 1 else ''}")
