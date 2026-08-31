"""PDF Conversion page."""
from pathlib import Path

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
    QSlider,
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.file_list import FileListWidget
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.conversion.conversion_service import ConversionService


class ConversionPage(QWidget):
    """Page for PDF conversion operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = ConversionService()
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

        # Header
        title = QLabel("PDF Conversion")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Convert between PDF and other formats with full control over quality and output.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Conversion mode
        mode_group = QGroupBox("Conversion Mode")
        mode_layout = QHBoxLayout(mode_group)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems([
            "PDF → Images (PNG/JPG/WEBP/TIFF/BMP)",
            "Images → PDF",
            "PDF → Word (DOCX)",
            "Word → PDF",
            "PDF → HTML",
            "PDF → Text",
        ])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self._mode_combo)
        layout.addWidget(mode_group)

        # Drop zone
        self._drop_zone = DropZone(
            accepted_extensions=[".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp", ".docx", ".txt", ".html"],
            multiple=True,
            label_text="Drag & Drop files here\nor click to browse",
        )
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self._drop_zone)

        # File list
        self._file_list = FileListWidget(title="Input Files")
        self._file_list.setMaximumHeight(200)
        layout.addWidget(self._file_list)

        # Settings
        settings_group = QGroupBox("Output Settings")
        settings_layout = QGridLayout(settings_group)

        # Format
        settings_layout.addWidget(QLabel("Output Format:"), 0, 0)
        self._format_combo = QComboBox()
        self._format_combo.addItems(["PNG", "JPEG", "WEBP", "TIFF", "BMP"])
        settings_layout.addWidget(self._format_combo, 0, 1)

        # DPI
        settings_layout.addWidget(QLabel("DPI:"), 0, 2)
        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(72, 600)
        self._dpi_spin.setValue(300)
        self._dpi_spin.setSuffix(" dpi")
        settings_layout.addWidget(self._dpi_spin, 0, 3)

        # Quality
        settings_layout.addWidget(QLabel("Quality:"), 1, 0)
        self._quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._quality_slider.setRange(10, 100)
        self._quality_slider.setValue(90)
        settings_layout.addWidget(self._quality_slider, 1, 1)
        self._quality_label = QLabel("90%")
        self._quality_slider.valueChanged.connect(
            lambda v: self._quality_label.setText(f"{v}%")
        )
        settings_layout.addWidget(self._quality_label, 1, 2)

        # Transparent background
        self._transparent_check = QCheckBox("Transparent Background (PNG only)")
        settings_layout.addWidget(self._transparent_check, 2, 0, 1, 2)

        # Overwrite protection
        self._overwrite_check = QCheckBox("Overwrite existing files")
        settings_layout.addWidget(self._overwrite_check, 2, 2, 1, 2)

        layout.addWidget(settings_group)

        # Output folder
        output_group = QGroupBox("Output Folder")
        output_layout = QHBoxLayout(output_group)

        self._output_path = QLineEdit()
        self._output_path.setPlaceholderText("Same as input file (default)")
        output_layout.addWidget(self._output_path)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(browse_btn)

        layout.addWidget(output_group)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self._convert_btn = QPushButton("Convert")
        self._convert_btn.setFixedSize(160, 44)
        self._convert_btn.clicked.connect(self._start_conversion)
        action_layout.addWidget(self._convert_btn)

        layout.addLayout(action_layout)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_mode_changed(self, index: int) -> None:
        """Update UI based on conversion mode."""
        # Show/hide image-specific options
        is_pdf_to_image = index == 0
        self._format_combo.setEnabled(is_pdf_to_image)
        self._dpi_spin.setEnabled(is_pdf_to_image)
        self._quality_slider.setEnabled(is_pdf_to_image or index == 1)
        self._transparent_check.setEnabled(is_pdf_to_image)

    def _on_files_dropped(self, files: list[str]) -> None:
        """Handle dropped files."""
        self._file_list.add_files(files)

    def _browse_output(self) -> None:
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._output_path.setText(folder)

    def _start_conversion(self) -> None:
        """Start the conversion process."""
        files = self._file_list.get_files()
        if not files:
            return

        mode = self._mode_combo.currentIndex()
        output_dir = self._output_path.text() or None
        fmt = self._format_combo.currentText().lower()
        dpi = self._dpi_spin.value()
        quality = self._quality_slider.value()
        transparent = self._transparent_check.isChecked()
        overwrite = self._overwrite_check.isChecked()

        self._progress = ProgressDialog(
            self, "Converting", f"Processing {len(files)} file(s)..."
        )
        self._progress.show()

        worker = Worker(
            self._service.convert_batch,
            files=files,
            mode=mode,
            output_dir=output_dir,
            fmt=fmt,
            dpi=dpi,
            quality=quality,
            transparent=transparent,
            overwrite=overwrite,
        )
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.progress_detail.connect(
            lambda v, msg: self._progress.set_message(msg)
        )
        worker.signals.finished.connect(self._on_conversion_done)
        worker.signals.error.connect(self._on_conversion_error)

        self._thread_pool.start(worker)

    def _on_conversion_done(self) -> None:
        """Handle conversion completion."""
        self._progress.close()

    def _on_conversion_error(self, error: str) -> None:
        """Handle conversion error."""
        self._progress.close()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Conversion Error", error.split("\n")[0])
