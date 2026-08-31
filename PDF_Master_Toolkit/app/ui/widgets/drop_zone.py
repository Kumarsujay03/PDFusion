"""Drag and drop zone widget."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class DropZone(QFrame):
    """A drag-and-drop zone for files."""

    files_dropped = Signal(list)

    def __init__(
        self,
        parent=None,
        accepted_extensions: Optional[list[str]] = None,
        multiple: bool = True,
        label_text: str = "Drag & Drop files here\nor click to browse",
    ) -> None:
        super().__init__(parent)
        self.accepted_extensions = accepted_extensions or [".pdf"]
        self.multiple = multiple

        self.setAcceptDrops(True)
        self.setObjectName("card")
        self.setMinimumHeight(150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_label = QLabel("📄")
        self._icon_label.setStyleSheet("font-size: 32pt; background: transparent;")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_label)

        self._text_label = QLabel(label_text)
        self._text_label.setObjectName("subtitle")
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setWordWrap(True)
        layout.addWidget(self._text_label)

        ext_text = ", ".join(self.accepted_extensions)
        self._ext_label = QLabel(f"Supported: {ext_text}")
        self._ext_label.setStyleSheet(
            "font-size: 9pt; color: #6c7086; background: transparent;"
        )
        self._ext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._ext_label)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            valid = any(
                Path(url.toLocalFile()).suffix.lower() in self.accepted_extensions
                for url in urls
            )
            if valid:
                event.acceptProposedAction()
                self.setStyleSheet(
                    self.styleSheet() + "DropZone { border: 2px dashed #89b4fa; }"
                )
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.setStyleSheet("")

    def dropEvent(self, event) -> None:
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        files = []
        for url in urls:
            path = Path(url.toLocalFile())
            if path.suffix.lower() in self.accepted_extensions:
                files.append(str(path))
                if not self.multiple:
                    break
        if files:
            self.files_dropped.emit(files)
            event.acceptProposedAction()

    def mousePressEvent(self, event) -> None:
        """Handle click to open file dialog."""
        from PySide6.QtWidgets import QFileDialog

        ext_filter = " ".join(f"*{ext}" for ext in self.accepted_extensions)
        filter_str = f"Supported Files ({ext_filter});;All Files (*.*)"

        if self.multiple:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "", filter_str
            )
        else:
            file, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", filter_str
            )
            files = [file] if file else []

        if files:
            self.files_dropped.emit(files)
