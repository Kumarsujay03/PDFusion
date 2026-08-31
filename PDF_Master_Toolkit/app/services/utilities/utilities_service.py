"""PDF Utilities service - page numbering, headers, repair, optimize, info."""
import os
from pathlib import Path
from typing import Callable, Optional

import fitz  # PyMuPDF


class UtilitiesService:
    """Service for PDF utility operations."""

    def add_page_numbers(
        self,
        file_path: str,
        position: int = 0,
        format_type: int = 0,
        start_number: int = 1,
        font_size: int = 11,
        skip_pages: str = "",
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Add page numbers to PDF.

        Positions: 0=bottom-center, 1=bottom-left, 2=bottom-right,
                   3=top-center, 4=top-left, 5=top-right
        Format: 0='1,2,3', 1='Page 1', 2='- 1 -', 3='i,ii,iii'
        """
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_numbered.pdf"

        # Parse skip pages
        skip_set: set[int] = set()
        if skip_pages.strip():
            try:
                for part in skip_pages.split(","):
                    skip_set.add(int(part.strip()) - 1)
            except ValueError:
                pass

        doc = fitz.open(file_path)
        try:
            total_pages = len(doc)

            for page_num in range(total_pages):
                if is_cancelled and is_cancelled():
                    break

                if page_num in skip_set:
                    continue

                page = doc[page_num]
                rect = page.rect
                number = start_number + page_num - len(
                    [s for s in skip_set if s < page_num]
                )

                # Format number
                if format_type == 0:
                    text = str(number)
                elif format_type == 1:
                    text = f"Page {number}"
                elif format_type == 2:
                    text = f"- {number} -"
                elif format_type == 3:
                    text = self._to_roman(number)
                else:
                    text = str(number)

                # Calculate position
                margin = 36  # 0.5 inch
                font = fitz.Font("helv")
                text_width = font.text_length(text, fontsize=font_size)

                if position == 0:  # Bottom center
                    x = (rect.width - text_width) / 2
                    y = rect.height - margin
                elif position == 1:  # Bottom left
                    x = margin
                    y = rect.height - margin
                elif position == 2:  # Bottom right
                    x = rect.width - text_width - margin
                    y = rect.height - margin
                elif position == 3:  # Top center
                    x = (rect.width - text_width) / 2
                    y = margin + font_size
                elif position == 4:  # Top left
                    x = margin
                    y = margin + font_size
                elif position == 5:  # Top right
                    x = rect.width - text_width - margin
                    y = margin + font_size
                else:
                    x = (rect.width - text_width) / 2
                    y = rect.height - margin

                page.insert_text(
                    fitz.Point(x, y),
                    text,
                    fontsize=font_size,
                    fontname="helv",
                    color=(0, 0, 0),
                )

                if progress_callback:
                    progress_callback(int(((page_num + 1) / total_pages) * 100))

            doc.save(str(output_path))
        finally:
            doc.close()

        return str(output_path)

    def add_header_footer(
        self,
        file_path: str,
        header_text: str = "",
        footer_text: str = "",
        font_size: int = 10,
        alignment: int = 0,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Add header and/or footer to PDF pages.

        Alignment: 0=center, 1=left, 2=right
        """
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_hf.pdf"

        doc = fitz.open(file_path)
        try:
            total_pages = len(doc)

            for page_num in range(total_pages):
                if is_cancelled and is_cancelled():
                    break

                page = doc[page_num]
                rect = page.rect
                margin = 36
                font = fitz.Font("helv")

                # Replace placeholders
                h_text = header_text.replace("{page}", str(page_num + 1)).replace(
                    "{total}", str(total_pages)
                )
                f_text = footer_text.replace("{page}", str(page_num + 1)).replace(
                    "{total}", str(total_pages)
                )

                # Header
                if h_text:
                    text_width = font.text_length(h_text, fontsize=font_size)
                    if alignment == 0:
                        x = (rect.width - text_width) / 2
                    elif alignment == 1:
                        x = margin
                    else:
                        x = rect.width - text_width - margin

                    page.insert_text(
                        fitz.Point(x, margin + font_size),
                        h_text,
                        fontsize=font_size,
                        fontname="helv",
                        color=(0, 0, 0),
                    )

                # Footer
                if f_text:
                    text_width = font.text_length(f_text, fontsize=font_size)
                    if alignment == 0:
                        x = (rect.width - text_width) / 2
                    elif alignment == 1:
                        x = margin
                    else:
                        x = rect.width - text_width - margin

                    page.insert_text(
                        fitz.Point(x, rect.height - margin),
                        f_text,
                        fontsize=font_size,
                        fontname="helv",
                        color=(0, 0, 0),
                    )

                if progress_callback:
                    progress_callback(int(((page_num + 1) / total_pages) * 100))

            doc.save(str(output_path))
        finally:
            doc.close()

        return str(output_path)

    def repair_pdf(
        self,
        file_path: str,
        flatten_forms: bool = False,
        flatten_annotations: bool = False,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Repair a PDF by re-saving with cleanup."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_repaired.pdf"

        if progress_callback:
            progress_callback(20)

        # Open with repair flag
        doc = fitz.open(file_path)
        try:
            if progress_callback:
                progress_callback(50)

            # Flatten annotations if requested
            if flatten_annotations:
                for page in doc:
                    annots = page.annots()
                    if annots:
                        for annot in annots:
                            annot.update()

            # Save with garbage collection and cleanup
            doc.save(
                str(output_path),
                garbage=4,
                deflate=True,
                clean=True,
            )
        finally:
            doc.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)

    def optimize_pdf(
        self,
        file_path: str,
        linearize: bool = True,
        clean: bool = True,
        deduplicate: bool = True,
        sanitize: bool = False,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Optimize a PDF for size and performance."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_optimized.pdf"

        if progress_callback:
            progress_callback(20)

        doc = fitz.open(file_path)
        try:
            if progress_callback:
                progress_callback(60)

            save_opts = {
                "garbage": 4 if deduplicate else 0,
                "deflate": True,
                "clean": clean,
                "linear": linearize,
            }

            doc.save(str(output_path), **save_opts)
        finally:
            doc.close()

        if progress_callback:
            progress_callback(100)

        return str(output_path)

    def get_pdf_info(self, file_path: str) -> str:
        """Get detailed information about a PDF file."""
        path = Path(file_path)
        file_size = path.stat().st_size

        doc = fitz.open(file_path)
        try:
            info_lines = [
                f"File: {path.name}",
                f"Path: {file_path}",
                f"File Size: {self._format_size(file_size)}",
                f"",
                f"--- Document Properties ---",
                f"Pages: {len(doc)}",
                f"PDF Version: {doc.metadata.get('format', 'Unknown') if doc.metadata else 'Unknown'}",
                f"Encrypted: {'Yes' if doc.is_encrypted else 'No'}",
                f"",
                f"--- Page Information ---",
            ]

            # Page sizes
            page_sizes: dict[str, int] = {}
            for page_num in range(min(len(doc), 100)):  # Limit to first 100 pages
                page = doc[page_num]
                rect = page.rect
                size_str = f"{rect.width:.0f} x {rect.height:.0f} pts ({rect.width/72:.1f} x {rect.height/72:.1f} in)"
                page_sizes[size_str] = page_sizes.get(size_str, 0) + 1

            for size, count in page_sizes.items():
                info_lines.append(f"  {size} ({count} page{'s' if count > 1 else ''})")

            # Metadata
            info_lines.append("")
            info_lines.append("--- Metadata ---")
            metadata = doc.metadata or {}
            for key, value in metadata.items():
                if value:
                    info_lines.append(f"  {key}: {value}")

            # Image count
            total_images = 0
            for page_num in range(min(len(doc), 50)):
                page = doc[page_num]
                total_images += len(page.get_images())

            info_lines.append("")
            info_lines.append("--- Statistics ---")
            info_lines.append(f"  Total Images: {total_images}")

            # Font information
            fonts: set[str] = set()
            for page_num in range(min(len(doc), 50)):
                page = doc[page_num]
                for font in page.get_fonts():
                    fonts.add(font[3] if len(font) > 3 else "Unknown")

            info_lines.append(f"  Fonts Used: {len(fonts)}")
            for font_name in sorted(fonts)[:20]:
                info_lines.append(f"    - {font_name}")

        finally:
            doc.close()

        return "\n".join(info_lines)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def _to_roman(num: int) -> str:
        """Convert integer to Roman numeral."""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
        roman = ""
        for i in range(len(val)):
            while num >= val[i]:
                roman += syms[i]
                num -= val[i]
        return roman
