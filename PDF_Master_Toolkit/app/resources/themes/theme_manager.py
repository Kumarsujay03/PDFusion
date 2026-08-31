"""Theme management for the application."""
from PySide6.QtWidgets import QApplication


DARK_THEME = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: #1e1e2e;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
    border-radius: 0px;
}

QFrame#sidebar QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    color: #bac2de;
    font-size: 10pt;
}

QFrame#sidebar QPushButton:hover {
    background-color: #313244;
    color: #cdd6f4;
}

QFrame#sidebar QPushButton:checked {
    background-color: #45475a;
    color: #89b4fa;
    font-weight: bold;
}

/* Content Area */
QFrame#content_area {
    background-color: #1e1e2e;
    border: none;
}

/* Cards */
QFrame#card {
    background-color: #313244;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #45475a;
}

QFrame#card:hover {
    border: 1px solid #89b4fa;
}

/* Buttons */
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 10pt;
}

QPushButton:hover {
    background-color: #b4d0fb;
}

QPushButton:pressed {
    background-color: #74a8fc;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#secondary {
    background-color: #45475a;
    color: #cdd6f4;
}

QPushButton#secondary:hover {
    background-color: #585b70;
}

QPushButton#danger {
    background-color: #f38ba8;
    color: #1e1e2e;
}

QPushButton#danger:hover {
    background-color: #f5a0ba;
}

/* Line Edit / Input */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #cdd6f4;
    font-size: 10pt;
    selection-background-color: #89b4fa;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #89b4fa;
}

/* ComboBox */
QComboBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #cdd6f4;
    font-size: 10pt;
}

QComboBox:hover {
    border: 2px solid #89b4fa;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    selection-background-color: #45475a;
    color: #cdd6f4;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #313244;
    border-radius: 6px;
    text-align: center;
    color: #cdd6f4;
    font-size: 9pt;
    height: 12px;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 6px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 8px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #bac2de;
    padding: 8px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #45475a;
    color: #89b4fa;
}

QTabBar::tab:hover {
    background-color: #45475a;
}

/* Group Box */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #cdd6f4;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}

/* Check Box & Radio */
QCheckBox, QRadioButton {
    color: #cdd6f4;
    spacing: 8px;
    font-size: 10pt;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #313244;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QRadioButton::indicator {
    border-radius: 9px;
}

/* Slider */
QSlider::groove:horizontal {
    background-color: #313244;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #89b4fa;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}

QSlider::sub-page:horizontal {
    background-color: #89b4fa;
    border-radius: 3px;
}

/* List Widget */
QListWidget {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #45475a;
    color: #89b4fa;
}

QListWidget::item:hover {
    background-color: #3b3d52;
}

/* Status Bar */
QStatusBar {
    background-color: #181825;
    color: #bac2de;
    border-top: 1px solid #313244;
    font-size: 9pt;
}

/* Tool Tip */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    font-size: 9pt;
}

/* Menu */
QMenu {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #45475a;
}

/* Label */
QLabel#title {
    font-size: 18pt;
    font-weight: bold;
    color: #cdd6f4;
}

QLabel#subtitle {
    font-size: 11pt;
    color: #a6adc8;
}

QLabel#section_title {
    font-size: 12pt;
    font-weight: bold;
    color: #cdd6f4;
}

/* Splitter */
QSplitter::handle {
    background-color: #313244;
    width: 2px;
}

/* Text Edit */
QTextEdit, QPlainTextEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px;
    color: #cdd6f4;
}

/* Table */
QTableWidget {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    gridline-color: #45475a;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #45475a;
}

QHeaderView::section {
    background-color: #181825;
    color: #cdd6f4;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #45475a;
    font-weight: bold;
}

/* File Dialog */
QFileDialog {
    background-color: #1e1e2e;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: #eff1f5;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #e6e9ef;
    border-right: 1px solid #ccd0da;
    border-radius: 0px;
}

QFrame#sidebar QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    color: #5c5f77;
    font-size: 10pt;
}

QFrame#sidebar QPushButton:hover {
    background-color: #ccd0da;
    color: #4c4f69;
}

QFrame#sidebar QPushButton:checked {
    background-color: #bcc0cc;
    color: #1e66f5;
    font-weight: bold;
}

/* Content Area */
QFrame#content_area {
    background-color: #eff1f5;
    border: none;
}

/* Cards */
QFrame#card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #ccd0da;
}

QFrame#card:hover {
    border: 1px solid #1e66f5;
}

/* Buttons */
QPushButton {
    background-color: #1e66f5;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 10pt;
}

QPushButton:hover {
    background-color: #4580f7;
}

QPushButton:pressed {
    background-color: #1555d4;
}

QPushButton:disabled {
    background-color: #ccd0da;
    color: #9ca0b0;
}

QPushButton#secondary {
    background-color: #ccd0da;
    color: #4c4f69;
}

QPushButton#secondary:hover {
    background-color: #bcc0cc;
}

QPushButton#danger {
    background-color: #d20f39;
    color: #ffffff;
}

QPushButton#danger:hover {
    background-color: #e83e5f;
}

/* Line Edit / Input */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 2px solid #ccd0da;
    border-radius: 8px;
    padding: 8px 12px;
    color: #4c4f69;
    font-size: 10pt;
    selection-background-color: #1e66f5;
    selection-color: #ffffff;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #1e66f5;
}

/* ComboBox */
QComboBox {
    background-color: #ffffff;
    border: 2px solid #ccd0da;
    border-radius: 8px;
    padding: 8px 12px;
    color: #4c4f69;
    font-size: 10pt;
}

QComboBox:hover {
    border: 2px solid #1e66f5;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    selection-background-color: #e6e9ef;
    color: #4c4f69;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #eff1f5;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #ccd0da;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #bcc0cc;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #eff1f5;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #ccd0da;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #bcc0cc;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #ccd0da;
    border-radius: 6px;
    text-align: center;
    color: #4c4f69;
    font-size: 9pt;
    height: 12px;
}

QProgressBar::chunk {
    background-color: #1e66f5;
    border-radius: 6px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #ccd0da;
    border-radius: 8px;
    background-color: #eff1f5;
}

QTabBar::tab {
    background-color: #e6e9ef;
    color: #5c5f77;
    padding: 8px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1e66f5;
}

QTabBar::tab:hover {
    background-color: #ccd0da;
}

/* Group Box */
QGroupBox {
    border: 1px solid #ccd0da;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #4c4f69;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
}

/* Check Box & Radio */
QCheckBox, QRadioButton {
    color: #4c4f69;
    spacing: 8px;
    font-size: 10pt;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #ccd0da;
    background-color: #ffffff;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #1e66f5;
    border-color: #1e66f5;
}

QRadioButton::indicator {
    border-radius: 9px;
}

/* Slider */
QSlider::groove:horizontal {
    background-color: #ccd0da;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #1e66f5;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}

QSlider::sub-page:horizontal {
    background-color: #1e66f5;
    border-radius: 3px;
}

/* List Widget */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #e6e9ef;
    color: #1e66f5;
}

QListWidget::item:hover {
    background-color: #f2f4f8;
}

/* Status Bar */
QStatusBar {
    background-color: #e6e9ef;
    color: #5c5f77;
    border-top: 1px solid #ccd0da;
    font-size: 9pt;
}

/* Tool Tip */
QToolTip {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px;
    font-size: 9pt;
}

/* Menu */
QMenu {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #e6e9ef;
}

/* Label */
QLabel#title {
    font-size: 18pt;
    font-weight: bold;
    color: #4c4f69;
}

QLabel#subtitle {
    font-size: 11pt;
    color: #6c6f85;
}

QLabel#section_title {
    font-size: 12pt;
    font-weight: bold;
    color: #4c4f69;
}

/* Splitter */
QSplitter::handle {
    background-color: #ccd0da;
    width: 2px;
}

/* Text Edit */
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 8px;
    color: #4c4f69;
}

/* Table */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    gridline-color: #ccd0da;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #e6e9ef;
}

QHeaderView::section {
    background-color: #e6e9ef;
    color: #4c4f69;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #ccd0da;
    font-weight: bold;
}
"""


class ThemeManager:
    """Manages application themes."""

    _instance = None

    def __new__(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_theme = "dark"
        return cls._instance

    @property
    def current_theme(self) -> str:
        return self._current_theme

    def apply_theme(self, theme: str) -> None:
        """Apply a theme to the application."""
        self._current_theme = theme
        app = QApplication.instance()
        if app:
            if theme == "dark":
                app.setStyleSheet(DARK_THEME)
            else:
                app.setStyleSheet(LIGHT_THEME)

    def toggle_theme(self) -> str:
        """Toggle between dark and light themes."""
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme

    def get_stylesheet(self, theme: str = None) -> str:
        """Get the stylesheet for a theme."""
        theme = theme or self._current_theme
        return DARK_THEME if theme == "dark" else LIGHT_THEME
