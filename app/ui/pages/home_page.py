"""Home page with quick actions and recent files."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QScrollArea,
)


class HomePage(QWidget):
    """Home page with quick access tools and recent files."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the home page UI."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Welcome header
        title = QLabel("Welcome to PDFusion")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Your all-in-one offline PDF solution. Select a tool to get started.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Quick Actions Grid
        section_label = QLabel("Quick Actions")
        section_label.setObjectName("section_title")
        layout.addWidget(section_label)

        grid = QGridLayout()
        grid.setSpacing(16)

        tools = [
            ("🔄", "Convert PDF", "Convert between PDF and other formats"),
            ("📦", "Compress PDF", "Reduce PDF file size"),
            ("✂️", "Split PDF", "Split PDF into multiple files"),
            ("📎", "Merge PDFs", "Combine multiple PDFs into one"),
            ("🔒", "Protect PDF", "Add password and encryption"),
            ("📝", "OCR", "Extract text from scanned PDFs"),
            ("🖼️", "Extract Images", "Extract images from PDF"),
            ("🛠️", "Repair PDF", "Fix corrupted PDF files"),
        ]

        for i, (icon, title_text, desc) in enumerate(tools):
            card = self._create_tool_card(icon, title_text, desc)
            grid.addWidget(card, i // 4, i % 4)

        layout.addLayout(grid)

        # Stats section
        layout.addSpacing(16)
        stats_label = QLabel("Application Info")
        stats_label.setObjectName("section_title")
        layout.addWidget(stats_label)

        info_frame = QFrame()
        info_frame.setObjectName("card")
        info_layout = QHBoxLayout(info_frame)

        stats = [
            ("7+", "Tool Categories"),
            ("50+", "Features"),
            ("100%", "Offline"),
            ("∞", "No Limits"),
        ]

        for value, label_text in stats:
            stat_widget = QVBoxLayout()
            val_label = QLabel(value)
            val_label.setStyleSheet(
                "font-size: 24pt; font-weight: bold; color: #89b4fa; background: transparent;"
            )
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(val_label)

            desc_label = QLabel(label_text)
            desc_label.setStyleSheet("font-size: 9pt; background: transparent;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(desc_label)

            info_layout.addLayout(stat_widget)

        layout.addWidget(info_frame)
        layout.addStretch()

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_tool_card(self, icon: str, title: str, description: str) -> QFrame:
        """Create a tool card widget."""
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(140)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28pt; background: transparent;")
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 11pt; font-weight: bold; background: transparent;"
        )
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 9pt; color: #6c7086; background: transparent;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()
        return card
