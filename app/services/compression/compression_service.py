"""PDF Compression service."""
import io
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional

import fitz
from PIL import Image


def _format_size(size_bytes: int) -> str:
    """Format a byte count as a human-readable string."""
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


class CompressionService:
    """Service for compressing PDF files."""

    # Compression presets: (image_quality, downsample_dpi). DPI 0 means no downsampling.
    PRESETS = {
        "lossless": (100, 0),
        "medium": (75, 200),
        "high": (50, 150),
        "extreme": (30, 100),
    }

    def compress_batch(
        self,
        files: list[str],
        settings: dict[str, Any],
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> list[dict[str, Any]]:
        """Compress multiple PDF files and return per-file size results."""
        results: list[dict[str, Any]] = []
        total = len(files)

        for i, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            percent = int((i / total) * 100)
            if progress_callback:
                progress_callback(percent)
            if progress_detail_callback:
                progress_detail_callback(percent, f"Compressing: {Path(file_path).name}")

            results.append(self.compress_single(file_path, settings, output_dir))

        if progress_callback:
            progress_callback(100)

        return results

    def compress_single(
        self,
        file_path: str,
        settings: dict[str, Any],
        output_dir: Optional[str] = None,
    ) -> dict[str, Any]:
        """Compress a single PDF file."""
        path = Path(file_path)
        out_dir = Path(output_dir) if output_dir else path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"{path.stem}_compressed.pdf"

        original_size = path.stat().st_size
        level = settings.get("level", "medium")

        if level == "target":
            target_mb = settings.get("target_size_mb", 5)
            return self._compress_to_target(file_path, str(output_path), target_mb, original_size)

        preset_quality, preset_dpi = self.PRESETS.get(level, self.PRESETS["medium"])
        if settings.get("image_quality"):
            preset_quality = settings["image_quality"]

        doc = fitz.open(file_path)
        try:
            if settings.get("downsample_images", True) and level != "lossless":
                self._compress_images(doc, preset_quality, preset_dpi)

            if settings.get("remove_metadata", False):
                doc.set_metadata({})

            doc.save(
                str(output_path),
                garbage=4 if settings.get("remove_duplicates", True) else 0,
                deflate=True,
                clean=True,
                linear=settings.get("linearize", False),
            )
        finally:
            doc.close()

        compressed_size = output_path.stat().st_size
        return self._result(file_path, str(output_path), original_size, compressed_size)

    def estimate_batch(
        self,
        files: list[str],
        settings: dict[str, Any],
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> dict[str, Any]:
        """Estimate compressed size for PDFs without writing final output files."""
        original_total = 0
        estimated_total = 0
        per_file: list[dict[str, Any]] = []
        total = len(files)

        for i, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            percent = int((i / total) * 100)
            if progress_callback:
                progress_callback(percent)
            if progress_detail_callback:
                progress_detail_callback(percent, f"Estimating: {Path(file_path).name}")

            path = Path(file_path)
            original_size = path.stat().st_size
            original_total += original_size

            estimated = self._estimate_single(file_path, settings, original_size)
            estimated_total += estimated
            per_file.append(self._result(file_path, "", original_size, estimated))

        if progress_callback:
            progress_callback(100)

        return self._summary(original_total, estimated_total, per_file)

    def _estimate_single(self, file_path: str, settings: dict[str, Any], original_size: int) -> int:
        """Compress into a temp file to measure the resulting size, then discard it."""
        level = settings.get("level", "medium")
        preset_quality, preset_dpi = self.PRESETS.get(level, self.PRESETS["medium"])
        if settings.get("image_quality"):
            preset_quality = settings["image_quality"]

        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.close()
        try:
            doc = fitz.open(file_path)
            try:
                if level == "target":
                    target_bytes = int(settings.get("target_size_mb", 5) * 1024 * 1024)
                    if original_size <= target_bytes:
                        return original_size
                    self._compress_images(doc, 40, 120)
                elif settings.get("downsample_images", True) and level != "lossless":
                    self._compress_images(doc, preset_quality, preset_dpi)

                if settings.get("remove_metadata", False):
                    doc.set_metadata({})

                doc.save(
                    tmp.name,
                    garbage=4 if settings.get("remove_duplicates", True) else 0,
                    deflate=True,
                    clean=True,
                )
            finally:
                doc.close()
            return Path(tmp.name).stat().st_size
        except Exception:
            return original_size
        finally:
            Path(tmp.name).unlink(missing_ok=True)

    def _compress_images(self, doc: fitz.Document, quality: int, max_dpi: int) -> None:
        """Recompress embedded images in a PDF, replacing them only when smaller."""
        for page in doc:
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image:
                        continue

                    image_bytes = base_image["image"]
                    width, height = base_image["width"], base_image["height"]
                    if width < 50 or height < 50:
                        continue

                    img = Image.open(io.BytesIO(image_bytes))

                    if max_dpi > 0:
                        rect = page.rect
                        current_dpi = max(width / (rect.width / 72), height / (rect.height / 72))
                        if current_dpi > max_dpi:
                            scale = max_dpi / current_dpi
                            img = img.resize(
                                (int(width * scale), int(height * scale)),
                                Image.Resampling.LANCZOS,
                            )

                    if img.mode == "RGBA":
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[3])
                        img = bg
                    elif img.mode not in ("RGB", "L"):
                        img = img.convert("RGB")

                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=quality, optimize=True)
                    new_bytes = buffer.getvalue()

                    if len(new_bytes) < len(image_bytes):
                        doc.update_stream(xref, new_bytes)
                except Exception:
                    continue

    def _compress_to_target(
        self,
        file_path: str,
        output_path: str,
        target_mb: float,
        original_size: int,
    ) -> dict[str, Any]:
        """Iteratively compress until the file drops below the target size."""
        target_bytes = int(target_mb * 1024 * 1024)

        if original_size <= target_bytes:
            shutil.copy2(file_path, output_path)
            return self._result(file_path, output_path, original_size, original_size)

        qualities = [80, 60, 40, 25, 15, 10]
        dpis = [200, 150, 120, 100, 80, 60]

        best_result = self._result(file_path, output_path, original_size, original_size)
        for quality, dpi in zip(qualities, dpis):
            doc = fitz.open(file_path)
            try:
                self._compress_images(doc, quality, dpi)
                doc.save(output_path, garbage=4, deflate=True, clean=True)
            finally:
                doc.close()

            compressed_size = Path(output_path).stat().st_size
            best_result = self._result(file_path, output_path, original_size, compressed_size)
            if compressed_size <= target_bytes:
                break

        return best_result

    @staticmethod
    def _result(input_path: str, output_path: str, original: int, compressed: int) -> dict[str, Any]:
        """Build a per-file result dict with formatted sizes and ratio."""
        ratio = round((1 - compressed / original) * 100, 1) if original > 0 else 0.0
        return {
            "input_path": input_path,
            "output_path": output_path,
            "original_size": original,
            "compressed_size": compressed,
            "original_size_str": _format_size(original),
            "compressed_size_str": _format_size(compressed),
            "ratio": ratio,
        }

    @staticmethod
    def _summary(original_total: int, estimated_total: int, per_file: list[dict[str, Any]]) -> dict[str, Any]:
        """Build an aggregate estimate summary."""
        ratio = round((1 - estimated_total / original_total) * 100, 1) if original_total > 0 else 0.0
        return {
            "original_total": original_total,
            "estimated_total": estimated_total,
            "original_total_str": _format_size(original_total),
            "estimated_total_str": _format_size(estimated_total),
            "ratio": ratio,
            "files": per_file,
        }
