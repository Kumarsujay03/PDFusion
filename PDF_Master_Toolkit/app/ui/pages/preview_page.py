"""PDF Preview page with viewer, search, and navigation."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
    QSplitter,
)

from app.ui.widgets.pdf_preview import PDFPreviewWidget
from app.ui.widgets.search_widget import SearchWidget


class PreviewPage(QWidget):
    """Page for PDF preview with zoom, search, and thumbnails."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        top_bar = QFrame()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("border-bottom: 1px solid #45475a; padding: 8px;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 8, 16, 8)

        title = QLabel("PDF Preview")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; background: transparent;")
        top_layout.addWidget(title)

        top_layout.addStretch()

        open_btn = QPushButton("Open PDF")
        open_btn.setFixedHeight(34)
        open_btn.clicked.connect(self._open_pdf)
        top_layout.addWidget(open_btn)

        layout.addWidget(top_bar)

        # Main splitter: preview + search panel
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Preview widget
        self._preview = PDFPreviewWidget()
        splitter.addWidget(self._preview)

        # Search panel (right side)
        search_panel = QFrame()
        search_panel.setFixedWidth(320)
        search_layout = QVBoxLayout(search_panel)
        search_layout.setContentsMargins(8, 8, 8, 8)

        search_title = QLabel("Search")
        search_title.setObjectName("section_title")
        search_layout.addWidget(search_title)

        self._search = SearchWidget()
        self._search.result_selected.connect(self._on_search_result)
        search_layout.addWidget(self._search)

        splitter.addWidget(search_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        layout.addWidget(splitter, 1)

    def _open_pdf(self) -> None:
        """Open a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf);;All Files (*.*)"
        )
        if file_path:
            self._preview.load_pdf(file_path)
            self._search.set_file(file_path)

    def _on_search_result(self, file_path: str, page_num: int) -> None:
        """Navigate to search result page."""
        self._preview._page_spin.setValue(page_num + 1)

    def load_file(self, file_path: str) -> None:
        """Load a file externally."""
        self._preview.load_pdf(file_path)
        self._search.set_file(file_path)
