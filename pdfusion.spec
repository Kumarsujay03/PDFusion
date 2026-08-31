# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for PDFusion."""

from pathlib import Path

block_cipher = None

project_root = Path(SPECPATH)
app_root = project_root / "app"

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(app_root / "config" / "settings.json"), "app/config"),
        (str(app_root / "resources"), "app/resources"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "fitz",
        "pikepdf",
        "pypdf",
        "PIL",
        "PIL.Image",
        "docx",
        "reportlab",
        "reportlab.lib.pagesizes",
        "reportlab.lib.units",
        "reportlab.platypus",
        "reportlab.lib.styles",
        "cv2",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "unittest",
        "test",
        "tests",
        "pytest",
        "matplotlib",
        "numpy.testing",
        "scipy",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDFusion",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PDFusion",
)
