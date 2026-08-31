"""OCR service - offline text recognition using Tesseract."""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional

import fitz  # PyMuPDF


class OCRService:
    """Service for OCR operations using Tesseract."""

    def __init__(self) -> None:
        self._tesseract_path: Optional[str] = None
        self._find_tesseract()

    def _find_tesseract(self) -> None:
        """Find Tesseract executable on the system."""
        # Check common Windows paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        ]

        for path in common_paths:
            if os.path.isfile(path):
                self._tesseract_path = path
                return

        # Check PATH
        tesseract_in_path = shutil.which("tesseract")
        if tesseract_in_path:
            self._tesseract_path = tesseract_in_path

    def check_tesseract(self) -> tuple[bool, str]:
        """Check if Tesseract is installed and return version."""
        if not self._tesseract_path:
            self._find_tesseract()

        if not self._tesseract_path:
            return False, ""

        try:
            result = subprocess.run(
                [self._tesseract_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version = result.stdout.split("\n")[0] if result.stdout else "unknown"
            return True, version
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False, ""

    def run_ocr_batch(
        self,
        files: list[str],
        language: str = "eng",
        output_type: int = 0,
        dpi: int = 300,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Run OCR on multiple files.

        output_type:
            0 - Searchable PDF
            1 - Text file
            2 - Both
        """
        if not self._tesseract_path:
            raise RuntimeError(
                "Tesseract OCR not found. Please install Tesseract and ensure it's in PATH."
            )

        all_text: list[str] = []
        total = len(files)

        for i, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            percent = int((i / total) * 100)
            if progress_callback:
                progress_callback(percent)
            if progress_detail_callback:
                progress_detail_callback(percent, f"OCR: {Path(file_path).name}")

            path = Path(file_path)
            out_dir = Path(output_dir) if output_dir else path.parent
            out_dir.mkdir(parents=True, exist_ok=True)

            if path.suffix.lower() == ".pdf":
                text = self._ocr_pdf(file_path, language, output_type, dpi, out_dir)
            else:
                text = self._ocr_image(file_path, language, output_type, dpi, out_dir)

            all_text.append(text)

        if progress_callback:
            progress_callback(100)

        return "\n\n".join(all_text)

    def _ocr_pdf(
        self,
        file_path: str,
        language: str,
        output_type: int,
        dpi: int,
        output_dir: Path,
    ) -> str:
        """OCR a PDF file - convert pages to images and run tesseract."""
        path = Path(file_path)
        all_text: list[str] = []

        doc = fitz.open(file_path)
        try:
            # Try using ocrmypdf if available for searchable PDF
            if output_type in (0, 2):
                output_pdf = output_dir / f"{path.stem}_ocr.pdf"
                try:
                    import ocrmypdf
                    ocrmypdf.ocr(
                        file_path,
                        str(output_pdf),
                        language=language,
                        deskew=True,
                        optimize=1,
                        skip_text=True,
                    )
                except ImportError:
                    # Fallback: manual page-by-page OCR
                    self._manual_ocr_pdf(doc, language, dpi, output_pdf)
                except Exception:
                    self._manual_ocr_pdf(doc, language, dpi, output_pdf)

            # Extract text for text output or preview
            if output_type in (1, 2):
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    zoom = dpi / 72.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)

                    import tempfile
                    temp_img = tempfile.NamedTemporaryFile(
                        suffix=".png", delete=False
                    )
                    pix.save(temp_img.name)
                    temp_img.close()

                    text = self._run_tesseract_text(temp_img.name, language)
                    all_text.append(f"--- Page {page_num + 1} ---\n{text}")

                    os.unlink(temp_img.name)

                # Save text file
                text_output = output_dir / f"{path.stem}_ocr.txt"
                with open(text_output, "w", encoding="utf-8") as f:
                    f.write("\n\n".join(all_text))

        finally:
            doc.close()

        return "\n\n".join(all_text) if all_text else "OCR completed."

    def _ocr_image(
        self,
        file_path: str,
        language: str,
        output_type: int,
        dpi: int,
        output_dir: Path,
    ) -> str:
        """OCR an image file."""
        path = Path(file_path)
        text = self._run_tesseract_text(file_path, language)

        if output_type in (0, 2):
            # Create searchable PDF from image
            output_pdf = output_dir / f"{path.stem}_ocr.pdf"
            self._run_tesseract_pdf(file_path, str(output_pdf.with_suffix("")), language)

        if output_type in (1, 2):
            # Save text file
            text_output = output_dir / f"{path.stem}_ocr.txt"
            with open(text_output, "w", encoding="utf-8") as f:
                f.write(text)

        return text

    def _run_tesseract_text(self, image_path: str, language: str) -> str:
        """Run Tesseract and return extracted text."""
        try:
            result = subprocess.run(
                [
                    self._tesseract_path,
                    image_path,
                    "stdout",
                    "-l", language,
                    "--psm", "3",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return f"[OCR Error: {e}]"

    def _run_tesseract_pdf(
        self, image_path: str, output_base: str, language: str
    ) -> None:
        """Run Tesseract to produce a searchable PDF."""
        try:
            subprocess.run(
                [
                    self._tesseract_path,
                    image_path,
                    output_base,
                    "-l", language,
                    "--psm", "3",
                    "pdf",
                ],
                capture_output=True,
                timeout=120,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def _manual_ocr_pdf(
        self,
        doc: fitz.Document,
        language: str,
        dpi: int,
        output_path: Path,
    ) -> None:
        """Manually OCR a PDF page by page and create searchable PDF."""
        import tempfile

        output_doc = fitz.open()
        zoom = dpi / 72.0

        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Save page as temp image
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            pix.save(temp_img.name)
            temp_img.close()

            # Create new page with same dimensions
            new_page = output_doc.new_page(
                width=page.rect.width, height=page.rect.height
            )

            # Insert the image
            new_page.insert_image(new_page.rect, filename=temp_img.name)

            # Get text and overlay as invisible text
            text = self._run_tesseract_text(temp_img.name, language)
            if text.strip():
                # Insert invisible text layer
                tw = fitz.TextWriter(new_page.rect)
                font = fitz.Font("helv")
                try:
                    tw.append(fitz.Point(0, 12), text[:1000], font=font, fontsize=1)
                    tw.write_text(new_page, opacity=0)
                except Exception:
                    pass

            os.unlink(temp_img.name)

        output_doc.save(str(output_path))
        output_doc.close()
