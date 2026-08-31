"""Global search widget for searching text in PDFs."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThreadPool
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QCheckBox,
)

import fitz  # PyMuPDF

from app.models.worker import Worker


class SearchWidget(QWidget):
    """Widget for searching text within PDF documents."""

    result_selected = Signal(str, int)  # file_path, page_number

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._thread_pool = QThreadPool.globalInstance()
        self._current_file: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search input
        search_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search in PDF...")
        self._search_input.returnPressed.connect(self._do_search)
        search_layout.addWidget(self._search_input)

        self._search_btn = QPushButton("Search")
        self._search_btn.setFixedWidth(80)
        self._search_btn.clicked.connect(self._do_search)
        search_layout.addWidget(self._search_btn)

        layout.addLayout(search_layout)

        # Options
        opts_layout = QHBoxLayout()
        self._case_sensitive = QCheckBox("Case Sensitive")
        opts_layout.addWidget(self._case_sensitive)

        self._whole_word = QCheckBox("Whole Words")
        opts_layout.addWidget(self._whole_word)

        opts_layout.addStretch()
        self._result_count = QLabel("")
        self._result_count.setStyleSheet("color: #6c7086; font-size: 9pt;")
        opts_layout.addWidget(self._result_count)

        layout.addLayout(opts_layout)

        # Results list
        self._results_list = QListWidget()
        self._results_list.itemDoubleClicked.connect(self._on_result_clicked)
        layout.addWidget(self._results_list)

    def set_file(self, file_path: str) -> None:
        """Set the PDF file to search in."""
        self._current_file = file_path
        self._results_list.clear()
        self._result_count.setText("")

    def _do_search(self) -> None:
        """Perform the search."""
        query = self._search_input.text().strip()
        if not query or not self._current_file:
            return

        self._results_list.clear()
        self._result_count.setText("Searching...")

        worker = Worker(
            self._search_pdf,
            file_path=self._current_file,
            query=query,
            case_sensitive=self._case_sensitive.isChecked(),
        )
        worker.signals.result.connect(self._on_search_complete)
        worker.signals.error.connect(self._on_search_error)
        self._thread_pool.start(worker)

    def _search_pdf(
        self,
        file_path: str,
        query: str,
        case_sensitive: bool = False,
        progress_callback=None,
        progress_detail_callback=None,
        is_cancelled=None,
    ) -> list[dict]:
        """Search for text in PDF pages."""
        results = []
        doc = fitz.open(file_path)
        try:
            flags = 0 if case_sensitive else fitz.TEXT_PRESERVE_WHITESPACE
            total = len(doc)

            for page_num in range(total):
                if is_cancelled and is_cancelled():
                    break

                page = doc[page_num]
                # Search on this page
                text_instances = page.search_for(query)

                if text_instances:
                    # Get surrounding context
                    page_text = page.get_text("text")
                    for rect in text_instances:
                        # Find context around the match
                        if not case_sensitive:
                            idx = page_text.lower().find(query.lower())
                        else:
                            idx = page_text.find(query)

                        if idx >= 0:
                            start = max(0, idx - 40)
                            end = min(len(page_text), idx + len(query) + 40)
                            context = page_text[start:end].replace("\n", " ").strip()
                            if start > 0:
                                context = "..." + context
                            if end < len(page_text):
                                context = context + "..."
                        else:
                            context = query

                        results.append({
                            "page": page_num,
                            "context": context,
                            "rect": (rect.x0, rect.y0, rect.x1, rect.y1),
                        })

                if progress_callback:
                    progress_callback(int(((page_num + 1) / total) * 100))

        finally:
            doc.close()

        return results

    def _on_search_complete(self, results) -> None:
        """Handle search results."""
        self._results_list.clear()

        if not results:
            self._result_count.setText("No results found")
            return

        self._result_count.setText(f"{len(results)} result(s) found")

        for result in results[:500]:  # Limit to 500 results
            page_num = result["page"]
            context = result["context"]
            item = QListWidgetItem(f"Page {page_num + 1}: {context}")
            item.setData(Qt.ItemDataRole.UserRole, result)
            self._results_list.addItem(item)

    def _on_search_error(self, error: str) -> None:
        self._result_count.setText("Search error")

    def _on_result_clicked(self, item: QListWidgetItem) -> None:
        """Handle result click."""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result and self._current_file:
            self.result_selected.emit(self._current_file, result["page"])
