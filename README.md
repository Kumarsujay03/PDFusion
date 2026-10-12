# PDFusion

A professional, all-in-one **offline** PDF utility for Windows, built with Python and PySide6 (Qt 6). Convert, compress, edit, secure, and OCR your PDFs entirely on your machine — no cloud services, no external APIs, no internet dependency.

## Features

### Conversion
- PDF to images (PNG, JPEG, WEBP, TIFF, BMP) with custom DPI and quality
- Images to PDF, Word to PDF, PDF to Word / HTML / Text
- Batch conversion with custom output folder and overwrite protection

### Compression
- Lossless, Medium, High, and Extreme presets
- **Compress to a target file size** (e.g. 1 MB, 5 MB, custom)
- Image downsampling, duplicate-object removal, metadata cleanup, linearization
- **Estimated size preview** — see the before/after size and ratio before you commit

### Editing
- Merge, split (by page, range, count, or size), extract, delete, rotate, reorder, reverse pages

### Security
- Add / remove passwords, AES-256 / AES-128 / RC4 encryption
- Set permissions (printing, copying, editing, annotations, forms)
- Text watermarks with adjustable opacity and rotation
- View, edit, and strip metadata

### OCR (offline via Tesseract)
- Scanned PDF and image to searchable PDF or text
- 10 languages including English, Hindi, Spanish, French, German, Chinese, Japanese, Korean, Arabic
- Multi-language recognition

### Image Tools
- Extract images from PDFs
- **Lossless image compression** (preserves exact pixels using optimized PNG / lossless WEBP)
- Resize, convert format, and batch process
- **Estimated size preview** for both PDFs and images

### Utilities
- Page numbering, headers/footers, repair, optimize, document info/statistics

### Interface
- Dark and light themes with instant switching
- Sidebar navigation, keyboard shortcuts, drag & drop everywhere
- PDF preview with zoom, pan, thumbnails, and page navigation
- Global text search, batch queue manager, and operation history
- Background workers with progress dialogs and cancellation

## Requirements

- Windows 10 / 11 (64-bit)
- Python 3.13+ (for running from source)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) — required only for OCR features
- [Ghostscript](https://www.ghostscript.com/) — optional, improves some PDF operations

## Installation (from source)

```bash
git clone https://github.com/Kumarsujay03/PDFusion.git
cd PDFusion
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Building a standalone Windows executable

The app can be packaged so it runs without Python installed.

**Folder build (recommended, faster startup):**

```bash
build.bat
```
Output: `dist\PDFusion\PDFusion.exe`

**Single-file build (portable):**

```bash
build_onefile.bat
```
Output: `dist\PDFusion.exe`

Both scripts install PyInstaller automatically if needed and invoke it via `python -m PyInstaller`, so no PATH configuration is required.

## Project Structure

```
PDFusion/
├── main.py                    # Entry point
├── requirements.txt
├── pdfusion.spec              # PyInstaller spec (folder build)
├── build.bat / build_onefile.bat
├── app/
│   ├── config/                # Settings and configuration manager
│   ├── models/                # Worker threads, history, service locator
│   ├── resources/themes/      # Dark and light stylesheets
│   ├── services/              # Business logic
│   │   ├── conversion/
│   │   ├── compression/
│   │   ├── pdf/               # Page editing
│   │   ├── security/
│   │   ├── ocr/
│   │   ├── image/
│   │   └── utilities/
│   └── ui/
│       ├── main_window.py
│       ├── pages/             # One page per tool category
│       └── widgets/           # Reusable widgets (drop zone, preview, toast, etc.)
└── tests/
```

## Architecture

- **MVC-style separation** — UI pages talk to service classes; services contain all PDF/image logic and no Qt code.
- **Dependency injection** via a service locator.
- **Background workers** keep the UI responsive; every long operation reports progress and supports cancellation.
- **Theme system** with runtime dark/light switching.

## Tech Stack

| Area | Library |
|------|---------|
| GUI | PySide6 (Qt 6) |
| PDF rendering | PyMuPDF (fitz) |
| PDF manipulation | pikepdf, pypdf |
| Image processing | Pillow |
| PDF generation | ReportLab |
| Word support | python-docx |
| OCR | Tesseract (via pytesseract / ocrmypdf) |

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request. Keep service logic free of Qt imports and match the existing code style (type hints, PEP 8).

## License

MIT License — see [LICENSE](LICENSE).
