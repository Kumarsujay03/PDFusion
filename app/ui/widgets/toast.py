"""Toast notification widget."""
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QGraphicsOpacityEffect


class Toast(QWidget):
    """A floating toast notification widget."""

    def __init__(
        self,
        parent: QWidget,
        message: str,
        duration: int = 3000,
        toast_type: str = "info",
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        colors = {
            "info": "#89b4fa",
            "success": "#a6e3a1",
            "warning": "#f9e2af",
            "error": "#f38ba8",
        }
        color = colors.get(toast_type, colors["info"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        label = QLabel(message)
        label.setStyleSheet(f"""
            QLabel {{
                color: #1e1e2e;
                font-size: 10pt;
                font-weight: bold;
                background: transparent;
            }}
        """)
        layout.addWidget(label)

        self.setStyleSheet(f"""
            Toast {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)

        self.adjustSize()

        # Opacity effect for fade animation
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        # Auto-hide timer
        QTimer.singleShot(duration, self._fade_out)

    def show_toast(self) -> None:
        """Show the toast with fade-in animation."""
        parent = self.parent()
        if parent:
            x = parent.width() - self.width() - 20
            y = parent.height() - self.height() - 40
            self.move(x, y)

        self._opacity_effect.setOpacity(0)
        self.show()

        self._fade_in_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in_anim.setDuration(200)
        self._fade_in_anim.setStartValue(0.0)
        self._fade_in_anim.setEndValue(1.0)
        self._fade_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_in_anim.start()

    def _fade_out(self) -> None:
        """Fade out and destroy."""
        self._fade_out_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out_anim.setDuration(300)
        self._fade_out_anim.setStartValue(1.0)
        self._fade_out_anim.setEndValue(0.0)
        self._fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out_anim.finished.connect(self.deleteLater)
        self._fade_out_anim.start()
