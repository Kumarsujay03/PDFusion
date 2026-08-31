"""Image Tools page - extract, replace, compress, resize images in PDFs."""
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
    QSlider,
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.file_list import FileListWidget
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.image.image_service import ImageService


class ImageToolsPage(QWidget):
    """Page for image-related PDF operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = ImageService()
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

        title = QLabel("Image Tools")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Extract, compress, resize, and convert images in PDF files.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._create_extract_tab(), "📤 Extract")
        tabs.addTab(self._create_compress_tab(), "📦 Compress")
        tabs.addTab(self._create_resize_tab(), "↔️ Resize")
        tabs.addTab(self._create_convert_tab(), "🔄 Convert")

        layout.addWidget(tabs)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_extract_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._extract_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=True,
            label_text="Drop PDFs to extract images from",
        )
        layout.addWidget(self._extract_drop)

        self._extract_list = FileListWidget(title="PDFs")
        self._extract_list.setMaximumHeight(150)
        self._extract_drop.files_dropped.connect(self._extract_list.add_files)
        layout.addWidget(self._extract_list)

        settings = QGroupBox("Extract Settings")
        s_layout = QGridLayout(settings)
        s_layout.addWidget(QLabel("Output Format:"), 0, 0)
        self._extract_format = QComboBox()
        self._extract_format.addItems(["PNG", "JPEG", "WEBP", "TIFF", "Original"])
        s_layout.addWidget(self._extract_format, 0, 1)

        s_layout.addWidget(QLabel("Min Size (px):"), 1, 0)
        self._extract_min_size = QSpinBox()
        self._extract_min_size.setRange(0, 1000)
        self._extract_min_size.setValue(50)
        s_layout.addWidget(self._extract_min_size, 1, 1)
        layout.addWidget(settings)

        out_layout = QHBoxLayout()
        out_layout.addWidget(QLabel("Output Folder:"))
        self._extract_output = QLineEdit()
        self._extract_output.setPlaceholderText("Same as input")
        out_layout.addWidget(self._extract_output)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.clicked.connect(
            lambda: self._browse_folder(self._extract_output)
        )
        out_layout.addWidget(browse_btn)
        layout.addLayout(out_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        extract_btn = QPushButton("Extract Images")
        extract_btn.setFixedSize(160, 40)
        extract_btn.clicked.connect(self._do_extract)
        btn_layout.addWidget(extract_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_compress_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._compress_drop = DropZone(
            accepted_extensions=[".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"],
            multiple=True,
            label_text="Drop images to compress",
        )
        layout.addWidget(self._compress_drop)

        self._compress_list = FileListWidget(title="Images")
        self._compress_list.setMaximumHeight(150)
        self._compress_drop.files_dropped.connect(self._compress_list.add_files)
        layout.addWidget(self._compress_list)

        settings = QGroupBox("Compression Settings")
        s_layout = QGridLayout(settings)

        self._compress_lossless = QCheckBox("Lossless (preserve exact quality)")
        self._compress_lossless.setToolTip(
            "Reduce file size without altering a single pixel. Uses optimized PNG / "
            "lossless WEBP encoding. Quality slider and resize are ignored."
        )
        self._compress_lossless.toggled.connect(self._on_lossless_toggled)
        s_layout.addWidget(self._compress_lossless, 0, 0, 1, 3)

        s_layout.addWidget(QLabel("Quality:"), 1, 0)
        self._compress_quality = QSlider(Qt.Orientation.Horizontal)
        self._compress_quality.setRange(10, 100)
        self._compress_quality.setValue(75)
        s_layout.addWidget(self._compress_quality, 1, 1)
        self._compress_quality_label = QLabel("75%")
        self._compress_quality.valueChanged.connect(
            lambda v: self._compress_quality_label.setText(f"{v}%")
        )
        s_layout.addWidget(self._compress_quality_label, 1, 2)

        self._compress_resize_check = QCheckBox("Also resize (max dimension)")
        s_layout.addWidget(self._compress_resize_check, 2, 0)
        self._compress_max_dim = QSpinBox()
        self._compress_max_dim.setRange(100, 10000)
        self._compress_max_dim.setValue(2000)
        self._compress_max_dim.setSuffix(" px")
        s_layout.addWidget(self._compress_max_dim, 2, 1)
        layout.addWidget(settings)

        # Estimated result preview
        self._compress_estimate = QLabel("Click \"Estimate Size\" to preview the result.")
        self._compress_estimate.setObjectName("subtitle")
        self._compress_estimate.setWordWrap(True)
        layout.addWidget(self._compress_estimate)
        self._compress_estimate_details = QLabel("")
        self._compress_estimate_details.setStyleSheet("color: #6c7086; font-size: 9pt;")
        self._compress_estimate_details.setWordWrap(True)
        layout.addWidget(self._compress_estimate_details)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        estimate_btn = QPushButton("Estimate Size")
        estimate_btn.setObjectName("secondary")
        estimate_btn.setFixedSize(160, 40)
        estimate_btn.clicked.connect(self._do_estimate_compress)
        btn_layout.addWidget(estimate_btn)
        compress_btn = QPushButton("Compress Images")
        compress_btn.setFixedSize(160, 40)
        compress_btn.clicked.connect(self._do_compress)
        btn_layout.addWidget(compress_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _on_lossless_toggled(self, lossless: bool) -> None:
        self._compress_quality.setEnabled(not lossless)
        self._compress_resize_check.setEnabled(not lossless)
        self._compress_max_dim.setEnabled(not lossless)

    def _create_resize_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._resize_drop = DropZone(
            accepted_extensions=[".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"],
            multiple=True,
            label_text="Drop images to resize",
        )
        layout.addWidget(self._resize_drop)

        self._resize_list = FileListWidget(title="Images")
        self._resize_list.setMaximumHeight(150)
        self._resize_drop.files_dropped.connect(self._resize_list.add_files)
        layout.addWidget(self._resize_list)

        settings = QGroupBox("Resize Settings")
        s_layout = QGridLayout(settings)

        s_layout.addWidget(QLabel("Mode:"), 0, 0)
        self._resize_mode = QComboBox()
        self._resize_mode.addItems(["By Percentage", "By Dimensions", "By Max Side"])
        s_layout.addWidget(self._resize_mode, 0, 1)

        s_layout.addWidget(QLabel("Width:"), 1, 0)
        self._resize_width = QSpinBox()
        self._resize_width.setRange(1, 20000)
        self._resize_width.setValue(1920)
        self._resize_width.setSuffix(" px")
        s_layout.addWidget(self._resize_width, 1, 1)

        s_layout.addWidget(QLabel("Height:"), 2, 0)
        self._resize_height = QSpinBox()
        self._resize_height.setRange(1, 20000)
        self._resize_height.setValue(1080)
        self._resize_height.setSuffix(" px")
        s_layout.addWidget(self._resize_height, 2, 1)

        s_layout.addWidget(QLabel("Percentage:"), 3, 0)
        self._resize_percent = QSpinBox()
        self._resize_percent.setRange(1, 500)
        self._resize_percent.setValue(50)
        self._resize_percent.setSuffix("%")
        s_layout.addWidget(self._resize_percent, 3, 1)

        self._resize_aspect = QCheckBox("Maintain aspect ratio")
        self._resize_aspect.setChecked(True)
        s_layout.addWidget(self._resize_aspect, 4, 0, 1, 2)

        layout.addWidget(settings)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        resize_btn = QPushButton("Resize Images")
        resize_btn.setFixedSize(160, 40)
        resize_btn.clicked.connect(self._do_resize)
        btn_layout.addWidget(resize_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_convert_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._convert_drop = DropZone(
            accepted_extensions=[".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"],
            multiple=True,
            label_text="Drop images to convert format",
        )
        layout.addWidget(self._convert_drop)

        self._convert_list = FileListWidget(title="Images")
        self._convert_list.setMaximumHeight(150)
        self._convert_drop.files_dropped.connect(self._convert_list.add_files)
        layout.addWidget(self._convert_list)

        settings = QGroupBox("Conversion Settings")
        s_layout = QHBoxLayout(settings)
        s_layout.addWidget(QLabel("Convert to:"))
        self._convert_format = QComboBox()
        self._convert_format.addItems(["PNG", "JPEG", "WEBP", "TIFF", "BMP"])
        s_layout.addWidget(self._convert_format)
        s_layout.addStretch()
        layout.addWidget(settings)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        convert_btn = QPushButton("Convert Images")
        convert_btn.setFixedSize(160, 40)
        convert_btn.clicked.connect(self._do_convert)
        btn_layout.addWidget(convert_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    # --- Actions ---

    def _browse_folder(self, line_edit: QLineEdit) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)

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

    def _do_extract(self) -> None:
        files = self._extract_list.get_files()
        if not files:
            return
        self._run_operation(
            self._service.extract_images,
            "Extracting Images",
            files=files,
            output_format=self._extract_format.currentText().lower(),
            min_size=self._extract_min_size.value(),
            output_dir=self._extract_output.text() or None,
        )

    def _compress_kwargs(self, files: list[str]) -> dict:
        lossless = self._compress_lossless.isChecked()
        max_dim = (
            self._compress_max_dim.value()
            if self._compress_resize_check.isChecked() and not lossless
            else None
        )
        return {
            "files": files,
            "quality": self._compress_quality.value(),
            "max_dimension": max_dim,
            "lossless": lossless,
        }

    def _do_compress(self) -> None:
        files = self._compress_list.get_files()
        if not files:
            return
        self._progress = ProgressDialog(self, "Compressing Images", "Processing...")
        self._progress.show()
        worker = Worker(self._service.compress_images, **self._compress_kwargs(files))
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.result.connect(self._show_compress_result)
        worker.signals.finished.connect(self._progress.close)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _do_estimate_compress(self) -> None:
        files = self._compress_list.get_files()
        if not files:
            return
        self._compress_estimate.setText("Estimating...")
        self._compress_estimate_details.setText("")
        self._progress = ProgressDialog(self, "Estimating", "Analyzing images...")
        self._progress.show()
        worker = Worker(self._service.estimate_image_compression, **self._compress_kwargs(files))
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.result.connect(self._show_compress_estimate)
        worker.signals.finished.connect(self._progress.close)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _show_compress_estimate(self, summary: dict) -> None:
        self._compress_estimate.setText(
            f"Estimated: {summary['original_total_str']} → {summary['estimated_total_str']} "
            f"({summary['ratio']:+.1f}% size change)"
        )
        self._compress_estimate_details.setText(self._format_image_lines(summary["files"]))

    def _show_compress_result(self, results: list) -> None:
        if not results:
            return
        from app.services.image.image_service import _format_size
        original = sum(r["original_size"] for r in results)
        compressed = sum(r["compressed_size"] for r in results)
        ratio = round((1 - compressed / original) * 100, 1) if original else 0.0
        self._compress_estimate.setText(
            f"Done: {_format_size(original)} → {_format_size(compressed)} ({ratio:+.1f}% size change)"
        )
        self._compress_estimate_details.setText(self._format_image_lines(results))

    @staticmethod
    def _format_image_lines(files: list) -> str:
        from pathlib import Path
        lines = []
        for r in files[:20]:
            name = Path(r["input_path"]).name
            lines.append(
                f"{name}: {r['original_size_str']} → {r['compressed_size_str']} ({r['ratio']:+.1f}%)"
            )
        if len(files) > 20:
            lines.append(f"... and {len(files) - 20} more")
        return "\n".join(lines)

    def _do_resize(self) -> None:
        files = self._resize_list.get_files()
        if not files:
            return
        self._run_operation(
            self._service.resize_images,
            "Resizing Images",
            files=files,
            mode=self._resize_mode.currentIndex(),
            width=self._resize_width.value(),
            height=self._resize_height.value(),
            percentage=self._resize_percent.value(),
            maintain_aspect=self._resize_aspect.isChecked(),
        )

    def _do_convert(self) -> None:
        files = self._convert_list.get_files()
        if not files:
            return
        self._run_operation(
            self._service.convert_format,
            "Converting Images",
            files=files,
            target_format=self._convert_format.currentText().lower(),
        )
