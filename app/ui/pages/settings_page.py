"""Settings page."""
from PySide6.QtCore import Qt, Signal
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
    QMessageBox,
)

from app.config import ConfigManager


class SettingsPage(QWidget):
    """Application settings page."""

    theme_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._config = ConfigManager()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Customize application behavior and defaults.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Appearance
        appear_group = QGroupBox("Appearance")
        appear_layout = QGridLayout(appear_group)

        appear_layout.addWidget(QLabel("Theme:"), 0, 0)
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Dark", "Light"])
        self._theme_combo.currentTextChanged.connect(self._on_theme_change)
        appear_layout.addWidget(self._theme_combo, 0, 1)

        appear_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self._font_size = QSpinBox()
        self._font_size.setRange(8, 16)
        self._font_size.setValue(10)
        self._font_size.setSuffix(" pt")
        appear_layout.addWidget(self._font_size, 1, 1)

        layout.addWidget(appear_group)

        # Default Conversion Settings
        conv_group = QGroupBox("Conversion Defaults")
        conv_layout = QGridLayout(conv_group)

        conv_layout.addWidget(QLabel("Default DPI:"), 0, 0)
        self._default_dpi = QSpinBox()
        self._default_dpi.setRange(72, 600)
        self._default_dpi.setValue(300)
        self._default_dpi.setSuffix(" dpi")
        conv_layout.addWidget(self._default_dpi, 0, 1)

        conv_layout.addWidget(QLabel("Default Quality:"), 1, 0)
        self._default_quality = QSpinBox()
        self._default_quality.setRange(10, 100)
        self._default_quality.setValue(90)
        self._default_quality.setSuffix("%")
        conv_layout.addWidget(self._default_quality, 1, 1)

        conv_layout.addWidget(QLabel("Default Format:"), 2, 0)
        self._default_format = QComboBox()
        self._default_format.addItems(["PNG", "JPEG", "WEBP", "TIFF"])
        conv_layout.addWidget(self._default_format, 2, 1)

        layout.addWidget(conv_group)

        # Compression Defaults
        comp_group = QGroupBox("Compression Defaults")
        comp_layout = QGridLayout(comp_group)

        comp_layout.addWidget(QLabel("Default Level:"), 0, 0)
        self._default_comp_level = QComboBox()
        self._default_comp_level.addItems(["Lossless", "Medium", "High", "Extreme"])
        comp_layout.addWidget(self._default_comp_level, 0, 1)

        comp_layout.addWidget(QLabel("Image Quality:"), 1, 0)
        self._default_img_quality = QSpinBox()
        self._default_img_quality.setRange(10, 100)
        self._default_img_quality.setValue(75)
        self._default_img_quality.setSuffix("%")
        comp_layout.addWidget(self._default_img_quality, 1, 1)

        layout.addWidget(comp_group)

        # OCR Defaults
        ocr_group = QGroupBox("OCR Defaults")
        ocr_layout = QGridLayout(ocr_group)

        ocr_layout.addWidget(QLabel("Default Language:"), 0, 0)
        self._default_ocr_lang = QComboBox()
        self._default_ocr_lang.addItems([
            "English", "Hindi", "Spanish", "French",
            "German", "Chinese", "Japanese", "Korean", "Arabic",
        ])
        ocr_layout.addWidget(self._default_ocr_lang, 0, 1)

        ocr_layout.addWidget(QLabel("OCR DPI:"), 1, 0)
        self._default_ocr_dpi = QSpinBox()
        self._default_ocr_dpi.setRange(150, 600)
        self._default_ocr_dpi.setValue(300)
        self._default_ocr_dpi.setSuffix(" dpi")
        ocr_layout.addWidget(self._default_ocr_dpi, 1, 1)

        layout.addWidget(ocr_group)

        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QGridLayout(perf_group)

        perf_layout.addWidget(QLabel("Max Threads:"), 0, 0)
        self._max_threads = QSpinBox()
        self._max_threads.setRange(1, 16)
        self._max_threads.setValue(4)
        perf_layout.addWidget(self._max_threads, 0, 1)

        perf_layout.addWidget(QLabel("Memory Limit:"), 1, 0)
        self._memory_limit = QSpinBox()
        self._memory_limit.setRange(512, 8192)
        self._memory_limit.setValue(2048)
        self._memory_limit.setSuffix(" MB")
        perf_layout.addWidget(self._memory_limit, 1, 1)

        layout.addWidget(perf_group)

        # Buttons
        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("danger")
        reset_btn.clicked.connect(self._reset_settings)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.setFixedSize(140, 40)
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _load_settings(self) -> None:
        """Load current settings into UI."""
        theme = self._config.get("theme.mode", "dark")
        self._theme_combo.setCurrentText(theme.capitalize())
        self._font_size.setValue(self._config.get("theme.font_size", 10))
        self._default_dpi.setValue(self._config.get("conversion.default_dpi", 300))
        self._default_quality.setValue(self._config.get("conversion.default_quality", 90))
        self._max_threads.setValue(self._config.get("performance.max_threads", 4))
        self._memory_limit.setValue(self._config.get("performance.memory_limit_mb", 2048))

    def _save_settings(self) -> None:
        """Save settings."""
        self._config.set("theme.font_size", self._font_size.value())
        self._config.set("conversion.default_dpi", self._default_dpi.value())
        self._config.set("conversion.default_quality", self._default_quality.value())
        self._config.set("conversion.default_format", self._default_format.currentText().lower())
        self._config.set("compression.default_level", self._default_comp_level.currentText().lower())
        self._config.set("compression.default_image_quality", self._default_img_quality.value())
        self._config.set("performance.max_threads", self._max_threads.value())
        self._config.set("performance.memory_limit_mb", self._memory_limit.value())

    def _on_theme_change(self, theme_text: str) -> None:
        theme = theme_text.lower()
        self.theme_changed.emit(theme)

    def _reset_settings(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._config.reset()
            self._load_settings()
