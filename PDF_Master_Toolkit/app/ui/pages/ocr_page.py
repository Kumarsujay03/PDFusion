"""OCR page - Offline text recognition using Tesseract."""
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
    QTextEdit,
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.file_list import FileListWidget
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.ocr.ocr_service import OCRService


class OCRPage(QWidget):
    """Page for OCR operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = OCRService()
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

        title = QLabel("OCR - Text Recognition")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Extract text from scanned PDFs and images using offline Tesseract OCR."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Status
        status_frame = QFrame()
        status_frame.setObjectName("card")
        status_layout = QHBoxLayout(status_frame)
        self._status_label = QLabel("Checking Tesseract installation...")
        status_layout.addWidget(self._status_label)
        self._check_btn = QPushButton("Check")
        self._check_btn.setObjectName("secondary")
        self._check_btn.setFixedWidth(80)
        self._check_btn.clicked.connect(self._check_tesseract)
        status_layout.addWidget(self._check_btn)
        layout.addWidget(status_frame)

        # Drop zone
        self._drop_zone = DropZone(
            accepted_extensions=[".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"],
            multiple=True,
            label_text="Drop PDFs or images for OCR",
        )
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self._drop_zone)

        self._file_list = FileListWidget(title="Files for OCR")
        self._file_list.setMaximumHeight(160)
        layout.addWidget(self._file_list)

        # OCR Settings
        settings_group = QGroupBox("OCR Settings")
        settings_layout = QGridLayout(settings_group)

        # Language
        settings_layout.addWidget(QLabel("Language:"), 0, 0)
        self._language_combo = QComboBox()
        self._language_combo.addItems([
            "English (eng)",
            "Hindi (hin)",
            "Spanish (spa)",
            "French (fra)",
            "German (deu)",
            "Chinese Simplified (chi_sim)",
            "Chinese Traditional (chi_tra)",
            "Japanese (jpn)",
            "Korean (kor)",
            "Arabic (ara)",
        ])
        settings_layout.addWidget(self._language_combo, 0, 1)

        # Multiple languages
        self._multi_lang_check = QCheckBox("Multi-language mode")
        settings_layout.addWidget(self._multi_lang_check, 1, 0)
        self._extra_langs = QLineEdit()
        self._extra_langs.setPlaceholderText("Additional languages (e.g., fra+deu)")
        self._extra_langs.setEnabled(False)
        self._multi_lang_check.toggled.connect(self._extra_langs.setEnabled)
        settings_layout.addWidget(self._extra_langs, 1, 1)

        # Output type
        settings_layout.addWidget(QLabel("Output Type:"), 2, 0)
        self._output_type = QComboBox()
        self._output_type.addItems([
            "Searchable PDF (text layer)",
            "Text file (.txt)",
            "Both (PDF + TXT)",
        ])
        settings_layout.addWidget(self._output_type, 2, 1)

        # DPI
        settings_layout.addWidget(QLabel("Processing DPI:"), 3, 0)
        self._ocr_dpi = QSpinBox()
        self._ocr_dpi.setRange(150, 600)
        self._ocr_dpi.setValue(300)
        self._ocr_dpi.setSuffix(" dpi")
        settings_layout.addWidget(self._ocr_dpi, 3, 1)

        # Page segmentation mode
        settings_layout.addWidget(QLabel("Page Segmentation:"), 4, 0)
        self._psm_combo = QComboBox()
        self._psm_combo.addItems([
            "Automatic (default)",
            "Single column",
            "Single block of text",
            "Single line",
            "Single word",
        ])
        settings_layout.addWidget(self._psm_combo, 4, 1)

        layout.addWidget(settings_group)

        # Output folder
        output_group = QGroupBox("Output")
        out_layout = QHBoxLayout(output_group)
        self._output_path = QLineEdit()
        self._output_path.setPlaceholderText("Same as input folder")
        out_layout.addWidget(self._output_path)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_output)
        out_layout.addWidget(browse_btn)
        layout.addWidget(output_group)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self._ocr_btn = QPushButton("Run OCR")
        self._ocr_btn.setFixedSize(160, 44)
        self._ocr_btn.clicked.connect(self._start_ocr)
        action_layout.addWidget(self._ocr_btn)
        layout.addLayout(action_layout)

        # Results preview
        results_group = QGroupBox("OCR Results Preview")
        results_layout = QVBoxLayout(results_group)
        self._results_text = QTextEdit()
        self._results_text.setReadOnly(True)
        self._results_text.setPlaceholderText("OCR results will appear here...")
        self._results_text.setMaximumHeight(200)
        results_layout.addWidget(self._results_text)
        layout.addWidget(results_group)

        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Check tesseract on load
        self._check_tesseract()

    def _check_tesseract(self) -> None:
        available, version = self._service.check_tesseract()
        if available:
            self._status_label.setText(f"✅ Tesseract {version} found")
            self._status_label.setStyleSheet("color: #a6e3a1; background: transparent;")
        else:
            self._status_label.setText("❌ Tesseract not found. Please install Tesseract OCR.")
            self._status_label.setStyleSheet("color: #f38ba8; background: transparent;")

    def _on_files_dropped(self, files: list[str]) -> None:
        self._file_list.add_files(files)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._output_path.setText(folder)

    def _start_ocr(self) -> None:
        files = self._file_list.get_files()
        if not files:
            return

        lang_map = {
            0: "eng", 1: "hin", 2: "spa", 3: "fra", 4: "deu",
            5: "chi_sim", 6: "chi_tra", 7: "jpn", 8: "kor", 9: "ara",
        }
        language = lang_map.get(self._language_combo.currentIndex(), "eng")

        if self._multi_lang_check.isChecked() and self._extra_langs.text():
            language = f"{language}+{self._extra_langs.text()}"

        output_type = self._output_type.currentIndex()
        dpi = self._ocr_dpi.value()
        output_dir = self._output_path.text() or None

        self._progress = ProgressDialog(
            self, "Running OCR", f"Processing {len(files)} file(s)..."
        )
        self._progress.show()

        worker = Worker(
            self._service.run_ocr_batch,
            files=files,
            language=language,
            output_type=output_type,
            dpi=dpi,
            output_dir=output_dir,
        )
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.progress_detail.connect(
            lambda v, msg: self._progress.set_message(msg)
        )
        worker.signals.result.connect(self._on_ocr_result)
        worker.signals.finished.connect(self._progress.close)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _on_ocr_result(self, result) -> None:
        if isinstance(result, str):
            self._results_text.setPlainText(result[:5000])

    def _on_error(self, error: str) -> None:
        self._progress.close()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "OCR Error", error.split("\n")[0])
