"""PDF Security service - encryption, passwords, watermarks, permissions, metadata."""
import io
from pathlib import Path
from typing import Any, Callable, Optional

import fitz  # PyMuPDF
import pikepdf


class SecurityService:
    """Service for PDF security operations."""

    def encrypt_pdf(
        self,
        file_path: str,
        user_password: str = "",
        owner_password: str = "",
        encryption: int = 0,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Encrypt a PDF with password protection.

        Args:
            encryption: 0=AES-256, 1=AES-128, 2=RC4-128
        """
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_encrypted.pdf"

        if progress_callback:
            progress_callback(20)

        # Map encryption levels
        enc_map = {
            0: pikepdf.Encryption(
                owner=owner_password or user_password,
                user=user_password,
                aes=True,
                R=6,  # AES-256
            ),
            1: pikepdf.Encryption(
                owner=owner_password or user_password,
                user=user_password,
                aes=True,
                R=4,  # AES-128
            ),
            2: pikepdf.Encryption(
                owner=owner_password or user_password,
                user=user_password,
                aes=False,
                R=4,  # RC4-128
            ),
        }

        enc = enc_map.get(encryption, enc_map[0])

        if progress_callback:
            progress_callback(50)

        pdf = pikepdf.open(file_path)
        try:
            pdf.save(str(output_path), encryption=enc)
        finally:
            pdf.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)

    def decrypt_pdf(
        self,
        file_path: str,
        password: str = "",
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Remove password/encryption from a PDF."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_decrypted.pdf"

        if progress_callback:
            progress_callback(30)

        pdf = pikepdf.open(file_path, password=password)
        try:
            pdf.save(str(output_path))
        finally:
            pdf.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)

    def set_permissions(
        self,
        file_path: str,
        permissions: dict[str, bool],
        owner_password: str = "",
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Set PDF permissions."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_restricted.pdf"

        if progress_callback:
            progress_callback(30)

        allow = pikepdf.Permissions(
            print_lowres=permissions.get("print", True),
            print_highres=permissions.get("print", True),
            modify_annotation=permissions.get("annotate", True),
            modify_form=permissions.get("forms", True),
            modify_assembly=permissions.get("edit", True),
            modify_other=permissions.get("edit", True),
            extract=permissions.get("copy", True),
            accessibility=True,
        )

        enc = pikepdf.Encryption(
            owner=owner_password or "owner",
            user="",
            allow=allow,
            aes=True,
            R=6,
        )

        if progress_callback:
            progress_callback(60)

        pdf = pikepdf.open(file_path)
        try:
            pdf.save(str(output_path), encryption=enc)
        finally:
            pdf.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)

    def add_watermark(
        self,
        file_path: str,
        text: str = "CONFIDENTIAL",
        font_size: int = 60,
        opacity: float = 0.3,
        rotation: int = -45,
        pages: str = "all",
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Add text watermark to PDF pages."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_watermarked.pdf"

        doc = fitz.open(file_path)
        try:
            total_pages = len(doc)

            # Parse page range
            if pages.strip().lower() == "all":
                page_nums = list(range(total_pages))
            else:
                from app.services.pdf.editing_service import EditingService
                page_nums = EditingService.parse_page_range(pages, total_pages)

            for i, page_num in enumerate(page_nums):
                if is_cancelled and is_cancelled():
                    break

                page = doc[page_num]
                rect = page.rect

                # Calculate center position
                center_x = rect.width / 2
                center_y = rect.height / 2

                # Create text writer
                tw = fitz.TextWriter(page.rect)

                # Use a built-in font
                font = fitz.Font("helv")

                # Calculate text position (centered)
                text_length = font.text_length(text, fontsize=font_size)
                x = center_x - text_length / 2
                y = center_y

                # Insert watermark text
                shape = page.new_shape()

                # Set transparency
                page.insert_text(
                    fitz.Point(x, y),
                    text,
                    fontsize=font_size,
                    fontname="helv",
                    rotate=rotation,
                    color=(0.5, 0.5, 0.5),
                    overlay=True,
                    render_mode=0,
                    fill_opacity=opacity,
                )

                if progress_callback:
                    progress_callback(int(((i + 1) / len(page_nums)) * 100))

            doc.save(str(output_path))
        finally:
            doc.close()

        return str(output_path)

    def get_metadata(self, file_path: str) -> dict[str, str]:
        """Get PDF metadata."""
        doc = fitz.open(file_path)
        try:
            metadata = doc.metadata or {}
            result = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
            }
        finally:
            doc.close()

        return result

    def set_metadata(
        self,
        file_path: str,
        metadata: dict[str, str],
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Set PDF metadata."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_meta.pdf"

        if progress_callback:
            progress_callback(30)

        doc = fitz.open(file_path)
        try:
            doc.set_metadata(metadata)
            doc.save(str(output_path))
        finally:
            doc.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)

    def remove_metadata(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Remove all metadata from PDF."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_clean.pdf"

        if progress_callback:
            progress_callback(30)

        doc = fitz.open(file_path)
        try:
            doc.set_metadata({
                "title": "",
                "author": "",
                "subject": "",
                "keywords": "",
                "creator": "",
                "producer": "",
            })
            # Also try to remove XMP metadata
            doc.del_xml_metadata()
            doc.save(str(output_path))
        finally:
            doc.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)
