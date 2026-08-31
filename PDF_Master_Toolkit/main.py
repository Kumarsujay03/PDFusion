"""PDFusion - Main Entry Point."""
import sys
import os
import logging
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))


def setup_logging() -> None:
    """Configure application logging."""
    log_dir = Path(__file__).parent / "app" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def setup_high_dpi() -> None:
    """Configure High DPI support."""
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")


def main() -> int:
    """Application entry point."""
    setup_logging()
    setup_high_dpi()

    logger = logging.getLogger("PDFusion")
    logger.info("Starting PDFusion...")

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("PDFusion")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PDFusion")

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Import and create main window
    from app.ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    logger.info("Application window ready.")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
