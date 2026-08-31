"""PDF Preview widget with zoom, pan, thumbnails, and page navigation."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSize, QPointF, QRectF
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QPainter,
    QWheelEvent,
    QMouseEvent,
    QPen,
    QColor,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QFrame,
    QScrollArea,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QSizePolicy,
    QComboBox,
)

import fitz  # PyMuPDF


class PDFGraphicsView(QGraphicsView):
    """Custom graphics view with zoom and pan support."""

    zoom_changed = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._zoom_factor = 1.0
        self._is_panning = False
        self._pan_start = QPointF()
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom with mouse wheel."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self._zoom_factor *= factor
            self._zoom_factor = max(0.1, min(10.0, self._zoom_factor))
            self.setTransform(
                self.transform().scale(factor, factor)
            )
            self.zoom_changed.emit(self._zoom_factor)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Start panning with middle button or space+left click."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Pan the view."""
        if self._is_panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y())
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Stop panning."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def set_zoom(self, factor: float) -> None:
        """Set absolute zoom level."""
        scale = factor / self._zoom_factor
        self._zoom_factor = factor
        self.setTransform(self.transform().scale(scale, scale))
        self.zoom_changed.emit(self._zoom_factor)

    def fit_width(self) -> None:
        """Fit the content to view width."""
        scene_rect = self.sceneRect()
        if scene_rect.width() > 0:
            view_width = self.viewport().width()
            factor = view_width / scene_rect.width()
            self.resetTransform()
            self._zoom_factor = factor
            self.scale(factor, factor)
            self.zoom_changed.emit(self._zoom_factor)

    def fit_page(self) -> None:
        """Fit the entire page in view."""
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        transform = self.transform()
        self._zoom_factor = transform.m11()
        self.zoom_changed.emit(self._zoom_factor)

    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor


class PDFPreviewWidget(QWidget):
    """Full PDF preview widget with thumbnails and navigation."""

    page_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._doc: Optional[fitz.Document] = None
        self._current_page = 0
        self._total_pages = 0
        self._file_path: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(44)
        toolbar.setStyleSheet(
            "QFrame { border-bottom: 1px solid #45475a; padding: 4px; }"
        )
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 4, 8, 4)

        # Navigation
        self._prev_btn = QPushButton("◀")
        self._prev_btn.setFixedSize(30, 30)
        self._prev_btn.setObjectName("secondary")
        self._prev_btn.clicked.connect(self._prev_page)
        tb_layout.addWidget(self._prev_btn)

        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(1)
        self._page_spin.setFixedWidth(70)
        self._page_spin.valueChanged.connect(self._go_to_page)
        tb_layout.addWidget(self._page_spin)

        self._total_label = QLabel("/ 0")
        self._total_label.setStyleSheet("background: transparent;")
        tb_layout.addWidget(self._total_label)

        self._next_btn = QPushButton("▶")
        self._next_btn.setFixedSize(30, 30)
        self._next_btn.setObjectName("secondary")
        self._next_btn.clicked.connect(self._next_page)
        tb_layout.addWidget(self._next_btn)

        tb_layout.addSpacing(20)

        # Zoom controls
        self._zoom_out_btn = QPushButton("−")
        self._zoom_out_btn.setFixedSize(30, 30)
        self._zoom_out_btn.setObjectName("secondary")
        self._zoom_out_btn.clicked.connect(self._zoom_out)
        tb_layout.addWidget(self._zoom_out_btn)

        self._zoom_combo = QComboBox()
        self._zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%", "300%"])
        self._zoom_combo.setCurrentIndex(2)
        self._zoom_combo.setFixedWidth(80)
        self._zoom_combo.currentTextChanged.connect(self._on_zoom_combo_changed)
        tb_layout.addWidget(self._zoom_combo)

        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setFixedSize(30, 30)
        self._zoom_in_btn.setObjectName("secondary")
        self._zoom_in_btn.clicked.connect(self._zoom_in)
        tb_layout.addWidget(self._zoom_in_btn)

        tb_layout.addSpacing(10)

        # Fit buttons
        self._fit_width_btn = QPushButton("Fit Width")
        self._fit_width_btn.setObjectName("secondary")
        self._fit_width_btn.setFixedHeight(30)
        self._fit_width_btn.clicked.connect(self._fit_width)
        tb_layout.addWidget(self._fit_width_btn)

        self._fit_page_btn = QPushButton("Fit Page")
        self._fit_page_btn.setObjectName("secondary")
        self._fit_page_btn.setFixedHeight(30)
        self._fit_page_btn.clicked.connect(self._fit_page)
        tb_layout.addWidget(self._fit_page_btn)

        # Rotate
        self._rotate_btn = QPushButton("↻")
        self._rotate_btn.setFixedSize(30, 30)
        self._rotate_btn.setObjectName("secondary")
        self._rotate_btn.setToolTip("Rotate view 90°")
        self._rotate_btn.clicked.connect(self._rotate_view)
        tb_layout.addWidget(self._rotate_btn)

        tb_layout.addStretch()

        layout.addWidget(toolbar)

        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Thumbnail sidebar
        self._thumb_list = QListWidget()
        self._thumb_list.setFixedWidth(140)
        self._thumb_list.setIconSize(QSize(100, 140))
        self._thumb_list.setSpacing(4)
        self._thumb_list.currentRowChanged.connect(self._on_thumb_clicked)
        splitter.addWidget(self._thumb_list)

        # Graphics view for page rendering
        self._scene = QGraphicsScene()
        self._view = PDFGraphicsView()
        self._view.setScene(self._scene)
        self._view.zoom_changed.connect(self._on_zoom_changed)
        splitter.addWidget(self._view)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([140, 600])

        layout.addWidget(splitter, 1)

        # Status bar
        self._status = QLabel("No PDF loaded")
        self._status.setStyleSheet(
            "padding: 4px 8px; font-size: 9pt; border-top: 1px solid #45475a; background: transparent;"
        )
        layout.addWidget(self._status)

    def load_pdf(self, file_path: str) -> None:
        """Load a PDF file for preview."""
        if self._doc:
            self._doc.close()

        self._file_path = file_path
        self._doc = fitz.open(file_path)
        self._total_pages = len(self._doc)
        self._current_page = 0

        self._page_spin.setMaximum(self._total_pages)
        self._page_spin.setValue(1)
        self._total_label.setText(f"/ {self._total_pages}")

        self._load_thumbnails()
        self._render_page(0)

        name = Path(file_path).name
        self._status.setText(f"{name} — {self._total_pages} pages")

    def _load_thumbnails(self) -> None:
        """Load page thumbnails."""
        self._thumb_list.clear()
        if not self._doc:
            return

        for page_num in range(min(self._total_pages, 200)):
            page = self._doc[page_num]
            # Render small thumbnail
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            img = QImage(
                pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(img)

            item = QListWidgetItem(f"Page {page_num + 1}")
            item.setIcon(pixmap)
            item.setData(Qt.ItemDataRole.UserRole, page_num)
            self._thumb_list.addItem(item)

    def _render_page(self, page_num: int) -> None:
        """Render a specific page at current zoom."""
        if not self._doc or page_num >= self._total_pages:
            return

        self._current_page = page_num
        page = self._doc[page_num]

        # Render at 150 DPI for good quality
        zoom = 150 / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = QImage(
            pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(img)

        self._scene.clear()
        self._scene.addPixmap(pixmap)
        self._scene.setSceneRect(QRectF(pixmap.rect()))

    def _prev_page(self) -> None:
        if self._current_page > 0:
            self._page_spin.setValue(self._current_page)  # 0-indexed to 1-indexed
            self._render_page(self._current_page - 1)
            self._thumb_list.setCurrentRow(self._current_page)
            self.page_changed.emit(self._current_page)

    def _next_page(self) -> None:
        if self._current_page < self._total_pages - 1:
            self._page_spin.setValue(self._current_page + 2)
            self._render_page(self._current_page + 1)
            self._thumb_list.setCurrentRow(self._current_page)
            self.page_changed.emit(self._current_page)

    def _go_to_page(self, page_num: int) -> None:
        page_idx = page_num - 1
        if 0 <= page_idx < self._total_pages:
            self._render_page(page_idx)
            self._thumb_list.setCurrentRow(page_idx)
            self.page_changed.emit(page_idx)

    def _on_thumb_clicked(self, row: int) -> None:
        if row >= 0:
            self._render_page(row)
            self._page_spin.setValue(row + 1)
            self.page_changed.emit(row)

    def _zoom_in(self) -> None:
        self._view.set_zoom(self._view.zoom_factor * 1.25)

    def _zoom_out(self) -> None:
        self._view.set_zoom(self._view.zoom_factor / 1.25)

    def _on_zoom_combo_changed(self, text: str) -> None:
        try:
            factor = int(text.replace("%", "")) / 100.0
            self._view.set_zoom(factor)
        except ValueError:
            pass

    def _on_zoom_changed(self, factor: float) -> None:
        percent = int(factor * 100)
        self._zoom_combo.setCurrentText(f"{percent}%")

    def _fit_width(self) -> None:
        self._view.fit_width()

    def _fit_page(self) -> None:
        self._view.fit_page()

    def _rotate_view(self) -> None:
        self._view.rotate(90)

    def close_document(self) -> None:
        """Close the current document."""
        if self._doc:
            self._doc.close()
            self._doc = None
        self._scene.clear()
        self._thumb_list.clear()
        self._total_pages = 0
        self._current_page = 0
        self._status.setText("No PDF loaded")

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def total_pages(self) -> int:
        return self._total_pages
