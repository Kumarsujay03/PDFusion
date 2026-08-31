"""Main application window."""
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QStackedWidget,
    QLabel,
    QStatusBar,
    QApplication,
    QSizePolicy,
    QScrollArea,
)

from app.config import ConfigManager
from app.resources.themes import ThemeManager
from app.ui.pages.home_page import HomePage
from app.ui.pages.conversion_page import ConversionPage
from app.ui.pages.compression_page import CompressionPage
from app.ui.pages.editing_page import EditingPage
from app.ui.pages.security_page import SecurityPage
from app.ui.pages.ocr_page import OCRPage
from app.ui.pages.image_tools_page import ImageToolsPage
from app.ui.pages.utilities_page import UtilitiesPage
from app.ui.pages.preview_page import PreviewPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.widgets.toast import Toast


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self) -> None:
        super().__init__()
        self._config = ConfigManager()
        self._theme = ThemeManager()
        self._setup_window()
        self._create_ui()
        self._create_statusbar()
        self._create_shortcuts()
        self._theme.apply_theme(self._config.get("theme.mode", "dark"))

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("PDFusion")
        self.setMinimumSize(
            self._config.get("app.min_width", 1000),
            self._config.get("app.min_height", 700),
        )
        self.resize(
            self._config.get("app.window_width", 1400),
            self._config.get("app.window_height", 900),
        )

    def _create_ui(self) -> None:
        """Create the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self._sidebar = self._create_sidebar()
        main_layout.addWidget(self._sidebar)

        # Content area
        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("content_area")

        # Create pages
        self._pages = {
            "home": HomePage(),
            "conversion": ConversionPage(),
            "compression": CompressionPage(),
            "editing": EditingPage(),
            "security": SecurityPage(),
            "ocr": OCRPage(),
            "image_tools": ImageToolsPage(),
            "utilities": UtilitiesPage(),
            "preview": PreviewPage(),
            "history": HistoryPage(),
            "settings": SettingsPage(),
        }

        for page in self._pages.values():
            self._content_stack.addWidget(page)

        # Connect settings page theme change signal
        if hasattr(self._pages["settings"], "theme_changed"):
            self._pages["settings"].theme_changed.connect(self._on_theme_changed)

        main_layout.addWidget(self._content_stack, 1)

    def _create_sidebar(self) -> QFrame:
        """Create the sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        # App title
        title_label = QLabel("PDFusion")
        title_label.setStyleSheet(
            "font-size: 16pt; font-weight: bold; padding: 8px 12px; background: transparent;"
        )
        layout.addWidget(title_label)

        subtitle_label = QLabel("Offline PDF Toolkit")
        subtitle_label.setStyleSheet(
            "font-size: 9pt; color: #6c7086; padding: 0px 12px 16px 12px; background: transparent;"
        )
        layout.addWidget(subtitle_label)

        # Navigation buttons
        self._nav_buttons: dict[str, QPushButton] = {}
        nav_items = [
            ("home", "🏠  Home"),
            ("conversion", "🔄  Conversion"),
            ("compression", "📦  Compression"),
            ("editing", "✂️  Editing"),
            ("security", "🔒  Security"),
            ("ocr", "📝  OCR"),
            ("image_tools", "🖼️  Image Tools"),
            ("utilities", "🛠️  Utilities"),
            ("preview", "👁️  Preview"),
            ("history", "📋  History"),
        ]

        for page_id, label in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, pid=page_id: self._navigate(pid))
            self._nav_buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #45475a; max-height: 1px;")
        layout.addWidget(sep)

        # Bottom actions
        settings_btn = QPushButton("⚙️  Settings")
        settings_btn.setCheckable(True)
        settings_btn.setFixedHeight(40)
        settings_btn.clicked.connect(lambda: self._navigate("settings"))
        self._nav_buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)

        theme_btn = QPushButton("🌙  Toggle Theme")
        theme_btn.setFixedHeight(40)
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn)

        # Set initial selection
        self._nav_buttons["home"].setChecked(True)

        return sidebar

    def _create_statusbar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self._status_label = QLabel("Ready")
        status_bar.addWidget(self._status_label, 1)

        self._version_label = QLabel(f"v{self._config.get('app.version', '1.0.0')}")
        status_bar.addPermanentWidget(self._version_label)

    def _create_shortcuts(self) -> None:
        """Create keyboard shortcuts."""
        shortcuts = {
            "Ctrl+1": lambda: self._navigate("home"),
            "Ctrl+2": lambda: self._navigate("conversion"),
            "Ctrl+3": lambda: self._navigate("compression"),
            "Ctrl+4": lambda: self._navigate("editing"),
            "Ctrl+5": lambda: self._navigate("security"),
            "Ctrl+6": lambda: self._navigate("ocr"),
            "Ctrl+7": lambda: self._navigate("image_tools"),
            "Ctrl+8": lambda: self._navigate("utilities"),
            "Ctrl+9": lambda: self._navigate("preview"),
            "Ctrl+0": lambda: self._navigate("history"),
            "Ctrl+,": lambda: self._navigate("settings"),
            "Ctrl+T": self._toggle_theme,
            "Ctrl+Q": self.close,
        }

        for shortcut, handler in shortcuts.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(handler)
            self.addAction(action)

    def _navigate(self, page_id: str) -> None:
        """Navigate to a page."""
        # Update button states
        for pid, btn in self._nav_buttons.items():
            btn.setChecked(pid == page_id)

        # Switch page
        page = self._pages.get(page_id)
        if page:
            self._content_stack.setCurrentWidget(page)
            self._status_label.setText(f"Current: {page_id.replace('_', ' ').title()}")

    def _toggle_theme(self) -> None:
        """Toggle application theme."""
        new_theme = self._theme.toggle_theme()
        self._config.set("theme.mode", new_theme)
        self.show_toast(f"Theme switched to {new_theme} mode", "info")

    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme change from settings page."""
        self._theme.apply_theme(theme)
        self._config.set("theme.mode", theme)

    def show_toast(self, message: str, toast_type: str = "info") -> None:
        """Show a toast notification."""
        toast = Toast(self, message, toast_type=toast_type)
        toast.show_toast()

    def set_status(self, message: str) -> None:
        """Update status bar message."""
        self._status_label.setText(message)
