"""PDF Editing page - merge, split, extract, rotate, reorder pages."""
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
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.file_list import FileListWidget
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.pdf.editing_service import EditingService


class EditingPage(QWidget):
    """Page for PDF editing operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = EditingService()
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
        title = QLabel("PDF Editing")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Merge, split, extract, rotate, and reorder PDF pages.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Tab widget for operations
        tabs = QTabWidget()

        # Merge Tab
        merge_widget = self._create_merge_tab()
        tabs.addTab(merge_widget, "📎 Merge")

        # Split Tab
        split_widget = self._create_split_tab()
        tabs.addTab(split_widget, "✂️ Split")

        # Extract Tab
        extract_widget = self._create_extract_tab()
        tabs.addTab(extract_widget, "📄 Extract")

        # Rotate Tab
        rotate_widget = self._create_rotate_tab()
        tabs.addTab(rotate_widget, "🔄 Rotate")

        # Reorder Tab
        reorder_widget = self._create_reorder_tab()
        tabs.addTab(reorder_widget, "↕️ Reorder")

        # Delete Tab
        delete_widget = self._create_delete_tab()
        tabs.addTab(delete_widget, "🗑️ Delete")

        layout.addWidget(tabs)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_merge_tab(self) -> QWidget:
        """Create merge PDFs tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        layout.addWidget(QLabel("Add PDF files to merge (order matters):"))

        self._merge_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=True,
            label_text="Drop PDFs here to merge",
        )
        layout.addWidget(self._merge_drop)

        self._merge_list = FileListWidget(title="PDFs to Merge")
        self._merge_drop.files_dropped.connect(self._merge_list.add_files)
        layout.addWidget(self._merge_list)

        # Output
        out_layout = QHBoxLayout()
        out_layout.addWidget(QLabel("Output:"))
        self._merge_output = QLineEdit()
        self._merge_output.setPlaceholderText("merged.pdf")
        out_layout.addWidget(self._merge_output)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.clicked.connect(lambda: self._browse_save(self._merge_output))
        out_layout.addWidget(browse_btn)
        layout.addLayout(out_layout)

        # Action
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        merge_btn = QPushButton("Merge PDFs")
        merge_btn.setFixedSize(140, 40)
        merge_btn.clicked.connect(self._do_merge)
        action_layout.addWidget(merge_btn)
        layout.addLayout(action_layout)

        return widget

    def _create_split_tab(self) -> QWidget:
        """Create split PDF tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._split_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to split",
        )
        layout.addWidget(self._split_drop)

        self._split_file = QLineEdit()
        self._split_file.setReadOnly(True)
        self._split_file.setPlaceholderText("No file selected")
        self._split_drop.files_dropped.connect(
            lambda files: self._split_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._split_file)

        # Split mode
        mode_group = QGroupBox("Split Mode")
        mode_layout = QVBoxLayout(mode_group)

        self._split_mode = QComboBox()
        self._split_mode.addItems([
            "Split into individual pages",
            "Split by page range",
            "Split by number of pages per file",
            "Split by file size",
        ])
        mode_layout.addWidget(self._split_mode)

        # Range input
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Pages/Range:"))
        self._split_range = QLineEdit()
        self._split_range.setPlaceholderText("e.g., 1-5, 6-10 or pages per file: 5")
        range_layout.addWidget(self._split_range)
        mode_layout.addLayout(range_layout)

        layout.addWidget(mode_group)

        # Output folder
        out_layout = QHBoxLayout()
        out_layout.addWidget(QLabel("Output Folder:"))
        self._split_output = QLineEdit()
        self._split_output.setPlaceholderText("Same as input")
        out_layout.addWidget(self._split_output)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.clicked.connect(
            lambda: self._browse_folder(self._split_output)
        )
        out_layout.addWidget(browse_btn)
        layout.addLayout(out_layout)

        # Action
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        split_btn = QPushButton("Split PDF")
        split_btn.setFixedSize(140, 40)
        split_btn.clicked.connect(self._do_split)
        action_layout.addWidget(split_btn)
        layout.addLayout(action_layout)

        return widget

    def _create_extract_tab(self) -> QWidget:
        """Create extract pages tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._extract_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to extract pages from",
        )
        layout.addWidget(self._extract_drop)

        self._extract_file = QLineEdit()
        self._extract_file.setReadOnly(True)
        self._extract_drop.files_dropped.connect(
            lambda files: self._extract_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._extract_file)

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Pages to Extract:"))
        self._extract_range = QLineEdit()
        self._extract_range.setPlaceholderText("e.g., 1,3,5-8,12")
        range_layout.addWidget(self._extract_range)
        layout.addLayout(range_layout)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        extract_btn = QPushButton("Extract Pages")
        extract_btn.setFixedSize(140, 40)
        extract_btn.clicked.connect(self._do_extract)
        action_layout.addWidget(extract_btn)
        layout.addLayout(action_layout)
        layout.addStretch()

        return widget

    def _create_rotate_tab(self) -> QWidget:
        """Create rotate pages tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._rotate_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to rotate pages",
        )
        layout.addWidget(self._rotate_drop)

        self._rotate_file = QLineEdit()
        self._rotate_file.setReadOnly(True)
        self._rotate_drop.files_dropped.connect(
            lambda files: self._rotate_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._rotate_file)

        options_layout = QGridLayout()
        options_layout.addWidget(QLabel("Pages:"), 0, 0)
        self._rotate_pages = QLineEdit()
        self._rotate_pages.setPlaceholderText("all (or e.g., 1,3,5-8)")
        options_layout.addWidget(self._rotate_pages, 0, 1)

        options_layout.addWidget(QLabel("Rotation:"), 1, 0)
        self._rotate_angle = QComboBox()
        self._rotate_angle.addItems(["90° Clockwise", "180°", "90° Counter-clockwise"])
        options_layout.addWidget(self._rotate_angle, 1, 1)

        layout.addLayout(options_layout)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        rotate_btn = QPushButton("Rotate Pages")
        rotate_btn.setFixedSize(140, 40)
        rotate_btn.clicked.connect(self._do_rotate)
        action_layout.addWidget(rotate_btn)
        layout.addLayout(action_layout)
        layout.addStretch()

        return widget

    def _create_reorder_tab(self) -> QWidget:
        """Create reorder pages tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._reorder_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to reorder pages",
        )
        layout.addWidget(self._reorder_drop)

        self._reorder_file = QLineEdit()
        self._reorder_file.setReadOnly(True)
        self._reorder_drop.files_dropped.connect(
            lambda files: self._reorder_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._reorder_file)

        layout.addWidget(QLabel("New page order (comma-separated):"))
        self._reorder_input = QLineEdit()
        self._reorder_input.setPlaceholderText("e.g., 3,1,2,5,4 or reverse")
        layout.addWidget(self._reorder_input)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        reorder_btn = QPushButton("Reorder Pages")
        reorder_btn.setFixedSize(140, 40)
        reorder_btn.clicked.connect(self._do_reorder)
        action_layout.addWidget(reorder_btn)
        layout.addLayout(action_layout)
        layout.addStretch()

        return widget

    def _create_delete_tab(self) -> QWidget:
        """Create delete pages tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._delete_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to delete pages from",
        )
        layout.addWidget(self._delete_drop)

        self._delete_file = QLineEdit()
        self._delete_file.setReadOnly(True)
        self._delete_drop.files_dropped.connect(
            lambda files: self._delete_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._delete_file)

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Pages to Delete:"))
        self._delete_range = QLineEdit()
        self._delete_range.setPlaceholderText("e.g., 1,3,5-8")
        range_layout.addWidget(self._delete_range)
        layout.addLayout(range_layout)

        action_layout = QHBoxLayout()
        action_layout.addStretch()
        delete_btn = QPushButton("Delete Pages")
        delete_btn.setObjectName("danger")
        delete_btn.setFixedSize(140, 40)
        delete_btn.clicked.connect(self._do_delete)
        action_layout.addWidget(delete_btn)
        layout.addLayout(action_layout)
        layout.addStretch()

        return widget

    # --- Action handlers ---

    def _browse_save(self, line_edit: QLineEdit) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "PDF Files (*.pdf)")
        if path:
            line_edit.setText(path)

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

    def _do_merge(self) -> None:
        files = self._merge_list.get_files()
        if len(files) < 2:
            return
        output = self._merge_output.text() or "merged.pdf"
        self._run_operation(
            self._service.merge_pdfs, "Merging PDFs", files=files, output_path=output
        )

    def _do_split(self) -> None:
        file = self._split_file.text()
        if not file:
            return
        mode = self._split_mode.currentIndex()
        range_text = self._split_range.text()
        output_dir = self._split_output.text() or None
        self._run_operation(
            self._service.split_pdf,
            "Splitting PDF",
            file_path=file,
            mode=mode,
            range_text=range_text,
            output_dir=output_dir,
        )

    def _do_extract(self) -> None:
        file = self._extract_file.text()
        if not file:
            return
        pages = self._extract_range.text()
        self._run_operation(
            self._service.extract_pages,
            "Extracting Pages",
            file_path=file,
            pages=pages,
        )

    def _do_rotate(self) -> None:
        file = self._rotate_file.text()
        if not file:
            return
        pages = self._rotate_pages.text() or "all"
        angle_map = {0: 90, 1: 180, 2: 270}
        angle = angle_map[self._rotate_angle.currentIndex()]
        self._run_operation(
            self._service.rotate_pages,
            "Rotating Pages",
            file_path=file,
            pages=pages,
            angle=angle,
        )

    def _do_reorder(self) -> None:
        file = self._reorder_file.text()
        if not file:
            return
        order = self._reorder_input.text()
        self._run_operation(
            self._service.reorder_pages,
            "Reordering Pages",
            file_path=file,
            order=order,
        )

    def _do_delete(self) -> None:
        file = self._delete_file.text()
        if not file:
            return
        pages = self._delete_range.text()
        self._run_operation(
            self._service.delete_pages,
            "Deleting Pages",
            file_path=file,
            pages=pages,
        )
