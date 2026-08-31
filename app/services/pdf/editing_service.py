"""PDF Editing service - merge, split, extract, rotate, reorder, delete pages."""
from pathlib import Path
from typing import Callable, Optional

import fitz  # PyMuPDF


class EditingService:
    """Service for PDF page manipulation operations."""

    @staticmethod
    def parse_page_range(range_text: str, total_pages: int) -> list[int]:
        """Parse page range string into list of 0-indexed page numbers.

        Supports: '1,3,5-8,12' or 'all' or 'reverse'
        """
        if not range_text or range_text.strip().lower() == "all":
            return list(range(total_pages))

        if range_text.strip().lower() == "reverse":
            return list(reversed(range(total_pages)))

        pages: list[int] = []
        parts = range_text.split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                try:
                    start, end = part.split("-", 1)
                    start_idx = int(start.strip()) - 1
                    end_idx = int(end.strip()) - 1
                    for p in range(start_idx, min(end_idx + 1, total_pages)):
                        if 0 <= p < total_pages and p not in pages:
                            pages.append(p)
                except ValueError:
                    continue
            else:
                try:
                    p = int(part) - 1
                    if 0 <= p < total_pages and p not in pages:
                        pages.append(p)
                except ValueError:
                    continue

        return pages

    def merge_pdfs(
        self,
        files: list[str],
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Merge multiple PDFs into one."""
        # Ensure output path is absolute
        output = Path(output_path)
        if not output.is_absolute():
            output = Path(files[0]).parent / output
        output.parent.mkdir(parents=True, exist_ok=True)

        merged_doc = fitz.open()
        try:
            total = len(files)
            for i, file_path in enumerate(files):
                if is_cancelled and is_cancelled():
                    break

                if progress_callback:
                    progress_callback(int((i / total) * 100))
                if progress_detail_callback:
                    progress_detail_callback(
                        int((i / total) * 100),
                        f"Adding: {Path(file_path).name}",
                    )

                doc = fitz.open(file_path)
                merged_doc.insert_pdf(doc)
                doc.close()

            merged_doc.save(str(output))
        finally:
            merged_doc.close()

        if progress_callback:
            progress_callback(100)

        return str(output)

    def split_pdf(
        self,
        file_path: str,
        mode: int,
        range_text: str = "",
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> list[str]:
        """Split PDF based on mode.

        Modes:
            0 - Individual pages
            1 - By page range (e.g., '1-5, 6-10')
            2 - By pages per file
            3 - By file size (approximate)
        """
        path = Path(file_path)
        out_dir = Path(output_dir) if output_dir else path.parent / f"{path.stem}_split"
        out_dir.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(file_path)
        output_files: list[str] = []

        try:
            total_pages = len(doc)

            if mode == 0:
                # Split into individual pages
                for i in range(total_pages):
                    if is_cancelled and is_cancelled():
                        break
                    if progress_callback:
                        progress_callback(int((i / total_pages) * 100))

                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=i, to_page=i)
                    out_path = out_dir / f"{path.stem}_page_{i + 1}.pdf"
                    new_doc.save(str(out_path))
                    new_doc.close()
                    output_files.append(str(out_path))

            elif mode == 1:
                # Split by ranges
                ranges = [r.strip() for r in range_text.split(",") if "-" in r.strip()]
                for idx, range_str in enumerate(ranges):
                    if is_cancelled and is_cancelled():
                        break

                    try:
                        start, end = range_str.split("-")
                        start_page = int(start.strip()) - 1
                        end_page = int(end.strip()) - 1
                        start_page = max(0, start_page)
                        end_page = min(total_pages - 1, end_page)

                        new_doc = fitz.open()
                        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
                        out_path = out_dir / f"{path.stem}_pages_{start_page + 1}-{end_page + 1}.pdf"
                        new_doc.save(str(out_path))
                        new_doc.close()
                        output_files.append(str(out_path))
                    except ValueError:
                        continue

                    if progress_callback:
                        progress_callback(int(((idx + 1) / len(ranges)) * 100))

            elif mode == 2:
                # Split by number of pages per file
                try:
                    pages_per_file = int(range_text.strip()) if range_text.strip() else 1
                except ValueError:
                    pages_per_file = 1

                pages_per_file = max(1, pages_per_file)
                file_count = 0

                for start in range(0, total_pages, pages_per_file):
                    if is_cancelled and is_cancelled():
                        break

                    end = min(start + pages_per_file - 1, total_pages - 1)
                    file_count += 1

                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start, to_page=end)
                    out_path = out_dir / f"{path.stem}_part_{file_count}.pdf"
                    new_doc.save(str(out_path))
                    new_doc.close()
                    output_files.append(str(out_path))

                    if progress_callback:
                        progress_callback(int((end / total_pages) * 100))

            elif mode == 3:
                # Split by file size (approximate using page count estimation)
                try:
                    target_size_mb = float(range_text.strip()) if range_text.strip() else 5
                except ValueError:
                    target_size_mb = 5

                file_size = path.stat().st_size
                avg_page_size = file_size / total_pages
                pages_per_chunk = max(1, int(target_size_mb * 1024 * 1024 / avg_page_size))

                file_count = 0
                for start in range(0, total_pages, pages_per_chunk):
                    if is_cancelled and is_cancelled():
                        break

                    end = min(start + pages_per_chunk - 1, total_pages - 1)
                    file_count += 1

                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start, to_page=end)
                    out_path = out_dir / f"{path.stem}_part_{file_count}.pdf"
                    new_doc.save(str(out_path))
                    new_doc.close()
                    output_files.append(str(out_path))

                    if progress_callback:
                        progress_callback(int((end / total_pages) * 100))

        finally:
            doc.close()

        if progress_callback:
            progress_callback(100)

        return output_files

    def extract_pages(
        self,
        file_path: str,
        pages: str,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Extract specific pages from a PDF."""
        path = Path(file_path)
        output = Path(output_path) if output_path else path.parent / f"{path.stem}_extracted.pdf"
        output.parent.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(file_path)
        try:
            page_nums = self.parse_page_range(pages, len(doc))
            new_doc = fitz.open()

            for i, page_num in enumerate(page_nums):
                if is_cancelled and is_cancelled():
                    break
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                if progress_callback:
                    progress_callback(int(((i + 1) / len(page_nums)) * 100))

            new_doc.save(str(output))
            new_doc.close()
        finally:
            doc.close()

        return str(output)

    def rotate_pages(
        self,
        file_path: str,
        pages: str = "all",
        angle: int = 90,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Rotate specified pages in a PDF."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_rotated.pdf"

        doc = fitz.open(file_path)
        try:
            page_nums = self.parse_page_range(pages, len(doc))

            for i, page_num in enumerate(page_nums):
                if is_cancelled and is_cancelled():
                    break
                page = doc[page_num]
                page.set_rotation(page.rotation + angle)
                if progress_callback:
                    progress_callback(int(((i + 1) / len(page_nums)) * 100))

            doc.save(str(output_path))
        finally:
            doc.close()

        return str(output_path)

    def reorder_pages(
        self,
        file_path: str,
        order: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Reorder pages in a PDF."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_reordered.pdf"

        doc = fitz.open(file_path)
        try:
            total_pages = len(doc)
            page_order = self.parse_page_range(order, total_pages)

            if not page_order:
                page_order = list(range(total_pages))

            new_doc = fitz.open()
            for i, page_num in enumerate(page_order):
                if is_cancelled and is_cancelled():
                    break
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                if progress_callback:
                    progress_callback(int(((i + 1) / len(page_order)) * 100))

            new_doc.save(str(output_path))
            new_doc.close()
        finally:
            doc.close()

        return str(output_path)

    def delete_pages(
        self,
        file_path: str,
        pages: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Delete specified pages from a PDF."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_modified.pdf"

        doc = fitz.open(file_path)
        try:
            total_pages = len(doc)
            pages_to_delete = set(self.parse_page_range(pages, total_pages))
            pages_to_keep = [i for i in range(total_pages) if i not in pages_to_delete]

            new_doc = fitz.open()
            for i, page_num in enumerate(pages_to_keep):
                if is_cancelled and is_cancelled():
                    break
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                if progress_callback:
                    progress_callback(int(((i + 1) / len(pages_to_keep)) * 100))

            new_doc.save(str(output_path))
            new_doc.close()
        finally:
            doc.close()

        return str(output_path)

    def insert_blank_page(
        self,
        file_path: str,
        after_page: int,
        width: float = 595,
        height: float = 842,
    ) -> str:
        """Insert a blank page after a specified page."""
        path = Path(file_path)
        output_path = path.parent / f"{path.stem}_modified.pdf"

        doc = fitz.open(file_path)
        try:
            doc.new_page(pno=after_page, width=width, height=height)
            doc.save(str(output_path))
        finally:
            doc.close()

        return str(output_path)

    def reverse_pages(self, file_path: str) -> str:
        """Reverse all pages in a PDF."""
        return self.reorder_pages(file_path, "reverse")
