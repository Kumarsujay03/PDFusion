"""PDF Security page - encryption, passwords, watermarks, permissions."""
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
    QTextEdit,
    QColorDialog,
)

from app.ui.widgets.drop_zone import DropZone
from app.ui.widgets.progress_dialog import ProgressDialog
from app.models.worker import Worker
from app.services.security.security_service import SecurityService


class SecurityPage(QWidget):
    """Page for PDF security operations."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = SecurityService()
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

        title = QLabel("PDF Security")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Protect your PDFs with passwords, encryption, watermarks, and permissions.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._create_password_tab(), "🔒 Password")
        tabs.addTab(self._create_permissions_tab(), "🛡️ Permissions")
        tabs.addTab(self._create_watermark_tab(), "💧 Watermark")
        tabs.addTab(self._create_metadata_tab(), "📋 Metadata")

        layout.addWidget(tabs)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_password_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._pwd_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to encrypt/decrypt",
        )
        layout.addWidget(self._pwd_drop)

        self._pwd_file = QLineEdit()
        self._pwd_file.setReadOnly(True)
        self._pwd_drop.files_dropped.connect(
            lambda files: self._pwd_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._pwd_file)

        # Action type
        action_group = QGroupBox("Action")
        action_layout = QHBoxLayout(action_group)
        self._pwd_action = QComboBox()
        self._pwd_action.addItems(["Add Password (Encrypt)", "Remove Password (Decrypt)"])
        self._pwd_action.currentIndexChanged.connect(self._on_pwd_action_changed)
        action_layout.addWidget(self._pwd_action)
        layout.addWidget(action_group)

        # Password inputs
        pwd_group = QGroupBox("Password Settings")
        pwd_layout = QGridLayout(pwd_group)

        pwd_layout.addWidget(QLabel("User Password:"), 0, 0)
        self._user_pwd = QLineEdit()
        self._user_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._user_pwd.setPlaceholderText("Required to open the PDF")
        pwd_layout.addWidget(self._user_pwd, 0, 1)

        pwd_layout.addWidget(QLabel("Owner Password:"), 1, 0)
        self._owner_pwd = QLineEdit()
        self._owner_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._owner_pwd.setPlaceholderText("Required to change permissions")
        pwd_layout.addWidget(self._owner_pwd, 1, 1)

        # Existing password (for decryption)
        pwd_layout.addWidget(QLabel("Current Password:"), 2, 0)
        self._current_pwd = QLineEdit()
        self._current_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._current_pwd.setPlaceholderText("Enter current password to decrypt")
        pwd_layout.addWidget(self._current_pwd, 2, 1)

        # Encryption level
        pwd_layout.addWidget(QLabel("Encryption:"), 3, 0)
        self._encryption_level = QComboBox()
        self._encryption_level.addItems(["AES-256 (Recommended)", "AES-128", "RC4-128"])
        pwd_layout.addWidget(self._encryption_level, 3, 1)

        layout.addWidget(pwd_group)

        # Action button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._pwd_btn = QPushButton("Encrypt PDF")
        self._pwd_btn.setFixedSize(160, 40)
        self._pwd_btn.clicked.connect(self._do_password)
        btn_layout.addWidget(self._pwd_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_permissions_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._perm_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to set permissions",
        )
        layout.addWidget(self._perm_drop)

        self._perm_file = QLineEdit()
        self._perm_file.setReadOnly(True)
        self._perm_drop.files_dropped.connect(
            lambda files: self._perm_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._perm_file)

        perm_group = QGroupBox("Permissions")
        perm_layout = QGridLayout(perm_group)

        self._perm_print = QCheckBox("Allow Printing")
        self._perm_print.setChecked(True)
        perm_layout.addWidget(self._perm_print, 0, 0)

        self._perm_copy = QCheckBox("Allow Copying")
        self._perm_copy.setChecked(True)
        perm_layout.addWidget(self._perm_copy, 0, 1)

        self._perm_edit = QCheckBox("Allow Editing")
        self._perm_copy.setChecked(True)
        perm_layout.addWidget(self._perm_edit, 1, 0)

        self._perm_annotate = QCheckBox("Allow Annotations")
        self._perm_annotate.setChecked(True)
        perm_layout.addWidget(self._perm_annotate, 1, 1)

        self._perm_forms = QCheckBox("Allow Form Filling")
        self._perm_forms.setChecked(True)
        perm_layout.addWidget(self._perm_forms, 2, 0)

        layout.addWidget(perm_group)

        # Owner password for setting permissions
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("Owner Password:"))
        self._perm_owner_pwd = QLineEdit()
        self._perm_owner_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_layout.addWidget(self._perm_owner_pwd)
        layout.addLayout(pwd_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        perm_btn = QPushButton("Apply Permissions")
        perm_btn.setFixedSize(160, 40)
        perm_btn.clicked.connect(self._do_permissions)
        btn_layout.addWidget(perm_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_watermark_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._wm_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to watermark",
        )
        layout.addWidget(self._wm_drop)

        self._wm_file = QLineEdit()
        self._wm_file.setReadOnly(True)
        self._wm_drop.files_dropped.connect(
            lambda files: self._wm_file.setText(files[0] if files else "")
        )
        layout.addWidget(self._wm_file)

        # Watermark type
        wm_group = QGroupBox("Watermark Settings")
        wm_layout = QGridLayout(wm_group)

        wm_layout.addWidget(QLabel("Type:"), 0, 0)
        self._wm_type = QComboBox()
        self._wm_type.addItems(["Text Watermark", "Image Watermark"])
        wm_layout.addWidget(self._wm_type, 0, 1)

        wm_layout.addWidget(QLabel("Text:"), 1, 0)
        self._wm_text = QLineEdit()
        self._wm_text.setPlaceholderText("CONFIDENTIAL")
        wm_layout.addWidget(self._wm_text, 1, 1)

        wm_layout.addWidget(QLabel("Font Size:"), 2, 0)
        self._wm_font_size = QSpinBox()
        self._wm_font_size.setRange(12, 200)
        self._wm_font_size.setValue(60)
        wm_layout.addWidget(self._wm_font_size, 2, 1)

        wm_layout.addWidget(QLabel("Opacity:"), 3, 0)
        self._wm_opacity = QSlider(Qt.Orientation.Horizontal)
        self._wm_opacity.setRange(5, 100)
        self._wm_opacity.setValue(30)
        wm_layout.addWidget(self._wm_opacity, 3, 1)
        self._wm_opacity_label = QLabel("30%")
        self._wm_opacity.valueChanged.connect(
            lambda v: self._wm_opacity_label.setText(f"{v}%")
        )
        wm_layout.addWidget(self._wm_opacity_label, 3, 2)

        wm_layout.addWidget(QLabel("Rotation:"), 4, 0)
        self._wm_rotation = QSpinBox()
        self._wm_rotation.setRange(-180, 180)
        self._wm_rotation.setValue(-45)
        self._wm_rotation.setSuffix("°")
        wm_layout.addWidget(self._wm_rotation, 4, 1)

        wm_layout.addWidget(QLabel("Pages:"), 5, 0)
        self._wm_pages = QLineEdit()
        self._wm_pages.setPlaceholderText("all (or e.g., 1,3,5-8)")
        wm_layout.addWidget(self._wm_pages, 5, 1)

        layout.addWidget(wm_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        wm_btn = QPushButton("Apply Watermark")
        wm_btn.setFixedSize(160, 40)
        wm_btn.clicked.connect(self._do_watermark)
        btn_layout.addWidget(wm_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def _create_metadata_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self._meta_drop = DropZone(
            accepted_extensions=[".pdf"],
            multiple=False,
            label_text="Drop a PDF to view/edit metadata",
        )
        layout.addWidget(self._meta_drop)

        self._meta_file = QLineEdit()
        self._meta_file.setReadOnly(True)
        self._meta_drop.files_dropped.connect(self._load_metadata)
        layout.addWidget(self._meta_file)

        # Metadata fields
        meta_group = QGroupBox("Metadata")
        meta_layout = QGridLayout(meta_group)

        fields = ["Title", "Author", "Subject", "Keywords", "Creator", "Producer"]
        self._meta_fields: dict[str, QLineEdit] = {}

        for i, field in enumerate(fields):
            meta_layout.addWidget(QLabel(f"{field}:"), i, 0)
            edit = QLineEdit()
            self._meta_fields[field.lower()] = edit
            meta_layout.addWidget(edit, i, 1)

        layout.addWidget(meta_group)

        btn_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove All Metadata")
        remove_btn.setObjectName("danger")
        remove_btn.clicked.connect(self._do_remove_metadata)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        save_btn = QPushButton("Save Metadata")
        save_btn.setFixedSize(160, 40)
        save_btn.clicked.connect(self._do_save_metadata)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    # --- Action handlers ---

    def _on_pwd_action_changed(self, index: int) -> None:
        is_encrypt = index == 0
        self._user_pwd.setEnabled(is_encrypt)
        self._owner_pwd.setEnabled(is_encrypt)
        self._encryption_level.setEnabled(is_encrypt)
        self._current_pwd.setEnabled(not is_encrypt)
        self._pwd_btn.setText("Encrypt PDF" if is_encrypt else "Decrypt PDF")

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

    def _do_password(self) -> None:
        file = self._pwd_file.text()
        if not file:
            return
        if self._pwd_action.currentIndex() == 0:
            self._run_operation(
                self._service.encrypt_pdf,
                "Encrypting PDF",
                file_path=file,
                user_password=self._user_pwd.text(),
                owner_password=self._owner_pwd.text(),
                encryption=self._encryption_level.currentIndex(),
            )
        else:
            self._run_operation(
                self._service.decrypt_pdf,
                "Decrypting PDF",
                file_path=file,
                password=self._current_pwd.text(),
            )

    def _do_permissions(self) -> None:
        file = self._perm_file.text()
        if not file:
            return
        permissions = {
            "print": self._perm_print.isChecked(),
            "copy": self._perm_copy.isChecked(),
            "edit": self._perm_edit.isChecked(),
            "annotate": self._perm_annotate.isChecked(),
            "forms": self._perm_forms.isChecked(),
        }
        self._run_operation(
            self._service.set_permissions,
            "Setting Permissions",
            file_path=file,
            permissions=permissions,
            owner_password=self._perm_owner_pwd.text(),
        )

    def _do_watermark(self) -> None:
        file = self._wm_file.text()
        if not file:
            return
        self._run_operation(
            self._service.add_watermark,
            "Adding Watermark",
            file_path=file,
            text=self._wm_text.text() or "CONFIDENTIAL",
            font_size=self._wm_font_size.value(),
            opacity=self._wm_opacity.value() / 100.0,
            rotation=self._wm_rotation.value(),
            pages=self._wm_pages.text() or "all",
        )

    def _load_metadata(self, files: list[str]) -> None:
        if files:
            self._meta_file.setText(files[0])
            metadata = self._service.get_metadata(files[0])
            for key, edit in self._meta_fields.items():
                edit.setText(metadata.get(key, ""))

    def _do_save_metadata(self) -> None:
        file = self._meta_file.text()
        if not file:
            return
        metadata = {key: edit.text() for key, edit in self._meta_fields.items()}
        self._run_operation(
            self._service.set_metadata,
            "Saving Metadata",
            file_path=file,
            metadata=metadata,
        )

    def _do_remove_metadata(self) -> None:
        file = self._meta_file.text()
        if not file:
            return
        self._run_operation(
            self._service.remove_metadata,
            "Removing Metadata",
            file_path=file,
        )
