"""PDF Compression page."""
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
    QRadioButton,
    QButtonGroup,
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.file_list import FileListWidget
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.compression.compression_service import CompressionService


class CompressionPage(QWidget):
    """Page for PDF compression operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = CompressionService()
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
        title = QLabel("PDF Compression")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Reduce PDF file size while maintaining quality. Choose a compression level or set a target size."
        )
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Drop zone
        self._drop_zone = DropZone(
            accepted_extensions=[".pdf"],
            multiple=True,
            label_text="Drag & Drop PDF files here",
        )
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        layout.addWidget(self._drop_zone)

        # File list
        self._file_list = FileListWidget(title="Files to Compress")
        self._file_list.setMaximumHeight(180)
        layout.addWidget(self._file_list)

        # Compression settings
        settings_group = QGroupBox("Compression Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Compression level radio buttons
        level_layout = QGridLayout()
        self._level_group = QButtonGroup(self)

        levels = [
            ("Lossless", "No quality loss, minimal size reduction"),
            ("Medium", "Good balance of size and quality"),
            ("High", "Significant size reduction, slight quality loss"),
            ("Extreme", "Maximum compression, noticeable quality loss"),
            ("Target Size", "Compress to a specific file size"),
        ]

        for i, (name, desc) in enumerate(levels):
            radio = QRadioButton(name)
            radio.setToolTip(desc)
            self._level_group.addButton(radio, i)
            level_layout.addWidget(radio, i // 3, i % 3)

        self._level_group.button(1).setChecked(True)
        self._level_group.idToggled.connect(self._on_level_changed)
        settings_layout.addLayout(level_layout)

        # Target size (hidden by default)
        self._target_frame = QFrame()
        target_layout = QHBoxLayout(self._target_frame)
        target_layout.setContentsMargins(0, 8, 0, 0)
        target_layout.addWidget(QLabel("Target Size:"))
        self._target_size_spin = QSpinBox()
        self._target_size_spin.setRange(1, 500)
        self._target_size_spin.setValue(5)
        self._target_size_spin.setSuffix(" MB")
        target_layout.addWidget(self._target_size_spin)
        target_layout.addStretch()
        self._target_frame.setVisible(False)
        settings_layout.addWidget(self._target_frame)

        layout.addWidget(settings_group)

        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        adv_layout = QGridLayout(advanced_group)

        self._downsample_check = QCheckBox("Downsample images")
        self._downsample_check.setChecked(True)
        adv_layout.addWidget(self._downsample_check, 0, 0)

        self._font_opt_check = QCheckBox("Optimize fonts")
        self._font_opt_check.setChecked(True)
        adv_layout.addWidget(self._font_opt_check, 0, 1)

        self._remove_metadata_check = QCheckBox("Remove metadata")
        adv_layout.addWidget(self._remove_metadata_check, 1, 0)

        self._remove_duplicates_check = QCheckBox("Remove duplicate objects")
        self._remove_duplicates_check.setChecked(True)
        adv_layout.addWidget(self._remove_duplicates_check, 1, 1)

        self._linearize_check = QCheckBox("Linearize (optimize for web)")
        adv_layout.addWidget(self._linearize_check, 2, 0)

        # Image quality slider
        adv_layout.addWidget(QLabel("Image Quality:"), 3, 0)
        self._img_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._img_quality_slider.setRange(10, 100)
        self._img_quality_slider.setValue(75)
        adv_layout.addWidget(self._img_quality_slider, 3, 1)
        self._img_quality_label = QLabel("75%")
        self._img_quality_slider.valueChanged.connect(
            lambda v: self._img_quality_label.setText(f"{v}%")
        )
        adv_layout.addWidget(self._img_quality_label, 3, 2)

        layout.addWidget(advanced_group)

        # Output folder
        output_group = QGroupBox("Output")
        output_layout = QHBoxLayout(output_group)
        self._output_path = QLineEdit()
        self._output_path.setPlaceholderText("Same folder as input (with _compressed suffix)")
        output_layout.addWidget(self._output_path)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_output)
        output_layout.addWidget(browse_btn)
        layout.addWidget(output_group)

        # Estimated size preview
        self._estimate_group = QGroupBox("Estimated Result")
        estimate_layout = QVBoxLayout(self._estimate_group)
        self._estimate_summary = QLabel("Click \"Estimate Size\" to preview the result.")
        self._estimate_summary.setObjectName("subtitle")
        self._estimate_summary.setWordWrap(True)
        estimate_layout.addWidget(self._estimate_summary)
        self._estimate_details = QLabel("")
        self._estimate_details.setStyleSheet("color: #6c7086; font-size: 9pt;")
        self._estimate_details.setWordWrap(True)
        estimate_layout.addWidget(self._estimate_details)
        layout.addWidget(self._estimate_group)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self._estimate_btn = QPushButton("Estimate Size")
        self._estimate_btn.setObjectName("secondary")
        self._estimate_btn.setFixedSize(160, 44)
        self._estimate_btn.clicked.connect(self._estimate_compression)
        action_layout.addWidget(self._estimate_btn)
        self._compress_btn = QPushButton("Compress")
        self._compress_btn.setFixedSize(160, 44)
        self._compress_btn.clicked.connect(self._start_compression)
        action_layout.addWidget(self._compress_btn)
        layout.addLayout(action_layout)

        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_level_changed(self, button_id: int, checked: bool) -> None:
        if checked:
            self._target_frame.setVisible(button_id == 4)

    def _on_files_dropped(self, files: list[str]) -> None:
        self._file_list.add_files(files)

    def _browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._output_path.setText(folder)

    def _gather_settings(self) -> dict:
        levels = ["lossless", "medium", "high", "extreme", "target"]
        level = levels[self._level_group.checkedId()]
        return {
            "level": level,
            "target_size_mb": self._target_size_spin.value() if level == "target" else None,
            "downsample_images": self._downsample_check.isChecked(),
            "optimize_fonts": self._font_opt_check.isChecked(),
            "remove_metadata": self._remove_metadata_check.isChecked(),
            "remove_duplicates": self._remove_duplicates_check.isChecked(),
            "linearize": self._linearize_check.isChecked(),
            "image_quality": self._img_quality_slider.value(),
        }

    def _estimate_compression(self) -> None:
        files = self._file_list.get_files()
        if not files:
            return

        self._estimate_summary.setText("Estimating...")
        self._estimate_details.setText("")

        self._progress = ProgressDialog(self, "Estimating", f"Analyzing {len(files)} file(s)...")
        self._progress.show()

        worker = Worker(
            self._service.estimate_batch,
            files=files,
            settings=self._gather_settings(),
        )
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.progress_detail.connect(lambda v, msg: self._progress.set_message(msg))
        worker.signals.result.connect(self._show_estimate)
        worker.signals.finished.connect(self._progress.close)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _start_compression(self) -> None:
        files = self._file_list.get_files()
        if not files:
            return

        output_dir = self._output_path.text() or None
        self._progress = ProgressDialog(self, "Compressing", f"Processing {len(files)} file(s)...")
        self._progress.show()

        worker = Worker(
            self._service.compress_batch,
            files=files,
            settings=self._gather_settings(),
            output_dir=output_dir,
        )
        worker.signals.progress.connect(self._progress.set_progress)
        worker.signals.progress_detail.connect(lambda v, msg: self._progress.set_message(msg))
        worker.signals.result.connect(self._show_result)
        worker.signals.finished.connect(self._progress.close)
        worker.signals.error.connect(self._on_error)
        self._thread_pool.start(worker)

    def _show_estimate(self, summary: dict) -> None:
        ratio = summary["ratio"]
        self._estimate_summary.setText(
            f"Estimated: {summary['original_total_str']} → {summary['estimated_total_str']} "
            f"({ratio:+.1f}% size change)"
        )
        self._estimate_details.setText(self._format_file_lines(summary["files"]))

    def _show_result(self, results: list) -> None:
        if not results:
            return
        original = sum(r["original_size"] for r in results)
        compressed = sum(r["compressed_size"] for r in results)
        from app.services.compression.compression_service import _format_size
        ratio = round((1 - compressed / original) * 100, 1) if original else 0.0
        self._estimate_summary.setText(
            f"Done: {_format_size(original)} → {_format_size(compressed)} "
            f"({ratio:+.1f}% size change)"
        )
        self._estimate_details.setText(self._format_file_lines(results))

    @staticmethod
    def _format_file_lines(files: list) -> str:
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

    def _on_error(self, error: str) -> None:
        self._progress.close()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Compression Error", error.split("\n")[0])
