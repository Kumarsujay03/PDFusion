"""PDF Utilities page - page numbering, headers, repair, optimize, etc."""
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QFrame,
    QScrollArea,
    QGroupBox,
    QGridLayout,
    QCheckBox,
    QFileDialog,
    QLineEdit,
    QTabWidget,
    QTextEdit,
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.utilities.utilities_service import UtilitiesService


class UtilitiesPage(QWidget):
    """Page for PDF utility operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = UtilitiesService()
        self._thread_pool = QThreadPool.globalInstance()
        self._setup_ui()

    def _setup_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("PDF Utilities")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Page numbering, headers/footers, repair, optimize, and more.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._create_numbering_tab(), "🔢 Page Numbers")
        tabs.addTab(self._create_header_footer_tab(), "📄 Header/Footer")
        tabs.addTab(self._create_repair_tab(), "🔧 Repair")
        tabs.addTab(self._create_optimize_tab(), "⚡ Optimize")
        tabs.addTab(self._create_info_tab(), "ℹ️ Info")

        layout.addWidget(tabs)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_numbering_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._num_drop = DropZone(
            accepted_extensions=[".pdf"], multiple=False,
            label_text="Drop a PDF to add page numbers",
        )
        layout.addWidget(self._num_drop)

        self._num_file = QLineEdit()
        self._num_file.setReadOnly(True)
        self._num_drop.files_dropped.connect(
            lambda files: self._num_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._num_file)

        settings = QGroupBox("Page Number Settings")
        s_layout = QGridLayout(settings)

        s_layout.addWidget(QLabel("Position:"), 0, 0)
        self._num_position = QComboBox()
        self._num_position.addItems([
            "Bottom Center", "Bottom Left", "Bottom Right",
            "Top Center", "Top Left", "Top Right",
        ])
        s_layout.addWidget(self._num_position, 0, 1)

        s_layout.addWidget(QLabel("Format:"), 1, 0)
        self._num_format = QComboBox()
        self._num_format.addItems([
            "1, 2, 3...", "Page 1, Page 2...",
            "- 1 -, - 2 -...", "i, ii, iii...",
        ])
        s_layout.addWidget(self._num_format, 1, 1)

        s_layout.addWidget(QLabel("Start From:"), 2, 0)
        self._num_start = QSpinBox()
        self._num_start.setRange(1, 9999)
        self._num_start.setValue(1)
        s_layout.addWidget(self._num_start, 2, 1)

        s_layout.addWidget(QLabel("Font Size:"), 3, 0)
        self._num_font_size = QSpinBox()
        self._num_font_size.setRange(6, 48)
        self._num_font_size.setValue(11)
        s_layout.addWidget(self._num_font_size, 3, 1)

        s_layout.addWidget(QLabel("Skip Pages:"), 4, 0)
        self._num_skip = QLineEdit()
        self._num_skip.setPlaceholderText("e.g., 1 (skip first page)")
        s_layout.addWidget(self._num_skip, 4, 1)

        layout.addWidget(settings)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        num_btn = QPushButton("Add Page Numbers")
        num_btn.setFixedSize(160, 40)
        num_btn.clicked.connect(self._do_numbering)
        btn_layout.addWidget(num_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_header_footer_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._hf_drop = DropZone(
            accepted_extensions=[".pdf"], multiple=False,
            label_text="Drop a PDF to add headers/footers",
        )
        layout.addWidget(self._hf_drop)

        self._hf_file = QLineEdit()
        self._hf_file.setReadOnly(True)
        self._hf_drop.files_dropped.connect(
            lambda files: self._hf_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._hf_file)

        settings = QGroupBox("Header & Footer")
        s_layout = QGridLayout(settings)

        s_layout.addWidget(QLabel("Header Text:"), 0, 0)
        self._header_text = QLineEdit()
        self._header_text.setPlaceholderText("Leave empty for no header")
        s_layout.addWidget(self._header_text, 0, 1)

        s_layout.addWidget(QLabel("Footer Text:"), 1, 0)
        self._footer_text = QLineEdit()
        self._footer_text.setPlaceholderText("Leave empty for no footer")
        s_layout.addWidget(self._footer_text, 1, 1)

        s_layout.addWidget(QLabel("Font Size:"), 2, 0)
        self._hf_font_size = QSpinBox()
        self._hf_font_size.setRange(6, 36)
        self._hf_font_size.setValue(10)
        s_layout.addWidget(self._hf_font_size, 2, 1)

        s_layout.addWidget(QLabel("Alignment:"), 3, 0)
        self._hf_align = QComboBox()
        self._hf_align.addItems(["Center", "Left", "Right"])
        s_layout.addWidget(self._hf_align, 3, 1)

        layout.addWidget(settings)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        hf_btn = QPushButton("Add Header/Footer")
        hf_btn.setFixedSize(160, 40)
        hf_btn.clicked.connect(self._do_header_footer)
        btn_layout.addWidget(hf_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_repair_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._repair_drop = DropZone(
            accepted_extensions=[".pdf"], multiple=True,
            label_text="Drop corrupted PDFs to repair",
        )
        layout.addWidget(self._repair_drop)

        self._repair_file = QLineEdit()
        self._repair_file.setReadOnly(True)
        self._repair_drop.files_dropped.connect(
            lambda files: self._repair_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._repair_file)

        self._flatten_forms = QCheckBox("Flatten form fields")
        layout.addWidget(self._flatten_forms)

        self._flatten_annotations = QCheckBox("Flatten annotations")
        layout.addWidget(self._flatten_annotations)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        repair_btn = QPushButton("Repair PDF")
        repair_btn.setFixedSize(160, 40)
        repair_btn.clicked.connect(self._do_repair)
        btn_layout.addWidget(repair_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_optimize_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._opt_drop = DropZone(
            accepted_extensions=[".pdf"], multiple=True,
            label_text="Drop PDFs to optimize",
        )
        layout.addWidget(self._opt_drop)

        self._opt_file = QLineEdit()
        self._opt_file.setReadOnly(True)
        self._opt_drop.files_dropped.connect(
            lambda files: self._opt_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._opt_file)

        options_group = QGroupBox("Optimization Options")
        opt_layout = QGridLayout(options_group)
        self._opt_linearize = QCheckBox("Linearize (Fast Web View)")
        self._opt_linearize.setChecked(True)
        opt_layout.addWidget(self._opt_linearize, 0, 0)

        self._opt_clean = QCheckBox("Clean unused objects")
        self._opt_clean.setChecked(True)
        opt_layout.addWidget(self._opt_clean, 0, 1)

        self._opt_deduplicate = QCheckBox("Deduplicate streams")
        self._opt_deduplicate.setChecked(True)
        opt_layout.addWidget(self._opt_deduplicate, 1, 0)

        self._opt_sanitize = QCheckBox("Sanitize content")
        opt_layout.addWidget(self._opt_sanitize, 1, 1)

        layout.addWidget(options_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        opt_btn = QPushButton("Optimize PDF")
        opt_btn.setFixedSize(160, 40)
        opt_btn.clicked.connect(self._do_optimize)
        btn_layout.addWidget(opt_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_info_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._info_drop = DropZone(
            accepted_extensions=[".pdf"], multiple=False,
            label_text="Drop a PDF to view information",
        )
        layout.addWidget(self._info_drop)

        self._info_file = QLineEdit()
        self._info_file.setReadOnly(True)
        self._info_drop.files_dropped.connect(self._show_info)
        layout.addWidget(self._info_file)

        self._info_text = QTextEdit()
        self._info_text.setReadOnly(True)
        self._info_text.setPlaceholderText("PDF information will appear here...")
        layout.addWidget(self._info_text)

        return widget

    # --- Actions ---

    def _run_operation(self, fn, title: str, **kwargs) -> None:
        self._progress = ProgressDialog(self, title, "Processing...")
        self._progress.show()
        worker = Worker(fn, **kwargs)
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.finished.connect(self._progress.close)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _on_error(self, error: str) -> None:
        self._progress.close()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", error.split("\n")[0])

    def _do_numbering(self) -> None:
        file = self._num_file.text()
        if not file:
            return
        self._run_operation(
            self._service.add_page_numbers,
            "Adding Page Numbers",
            file_path=file,
            position=self._num_position.currentIndex(),
            format_type=self._num_format.currentIndex(),
            start_number=self._num_start.value(),
            font_size=self._num_font_size.value(),
            skip_pages=self._num_skip.text(),
        )

    def _do_header_footer(self) -> None:
        file = self._hf_file.text()
        if not file:
            return
        self._run_operation(
            self._service.add_header_footer,
            "Adding Header/Footer",
            file_path=file,
            header_text=self._header_text.text(),
            footer_text=self._footer_text.text(),
            font_size=self._hf_font_size.value(),
            alignment=self._hf_align.currentIndex(),
        )

    def _do_repair(self) -> None:
        file = self._repair_file.text()
        if not file:
            return
        self._run_operation(
            self._service.repair_pdf,
            "Repairing PDF",
            file_path=file,
            flatten_forms=self._flatten_forms.isChecked(),
            flatten_annotations=self._flatten_annotations.isChecked(),
        )

    def _do_optimize(self) -> None:
        file = self._opt_file.text()
        if not file:
            return
        self._run_operation(
            self._service.optimize_pdf,
            "Optimizing PDF",
            file_path=file,
            linearize=self._opt_linearize.isChecked(),
            clean=self._opt_clean.isChecked(),
            deduplicate=self._opt_deduplicate.isChecked(),
            sanitize=self._opt_sanitize.isChecked(),
        )

    def _show_info(self, files: list[str]) -> None:
        if not files:
            return
        self._info_file.setText(files[0])
        info = self._service.get_pdf_info(files[0])
        self._info_text.setPlainText(info)
