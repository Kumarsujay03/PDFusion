"""Image service - extract, compress, resize, convert images."""
import io
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


class ImageService:
    """Service for image-related operations on PDFs and standalone images."""

    def extract_images(
        self,
        files: list[str],
        output_format: str = "png",
        min_size: int = 50,
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> list[str]:
        """Extract images embedded in PDF files."""
        output_files: list[str] = []
        total = len(files)

        for file_idx, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            path = Path(file_path)
            out_dir = Path(output_dir) if output_dir else path.parent / f"{path.stem}_images"
            out_dir.mkdir(parents=True, exist_ok=True)

            if progress_detail_callback:
                progress_detail_callback(
                    int((file_idx / total) * 100),
                    f"Extracting from: {path.name}",
                )

            doc = fitz.open(file_path)
            try:
                img_count = 0
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    for img_info in page.get_images(full=True):
                        if is_cancelled and is_cancelled():
                            break

                        xref = img_info[0]
                        try:
                            base_image = doc.extract_image(xref)
                            if not base_image:
                                continue

                            if base_image["width"] < min_size or base_image["height"] < min_size:
                                continue

                            img = Image.open(io.BytesIO(base_image["image"]))
                            img_count += 1

                            ext = base_image.get("ext", "png") if output_format == "original" else output_format
                            out_path = out_dir / f"{path.stem}_p{page_num + 1}_img{img_count}.{ext}"

                            save_format = "JPEG" if ext in ("jpg", "jpeg") else ext.upper()
                            if save_format == "JPEG":
                                img = self._flatten_to_rgb(img)
                            img.save(str(out_path), save_format, quality=95)
                            output_files.append(str(out_path))
                        except Exception:
                            continue
            finally:
                doc.close()

            if progress_callback:
                progress_callback(int(((file_idx + 1) / total) * 100))

        return output_files

    def compress_images(
        self,
        files: list[str],
        quality: int = 75,
        max_dimension: Optional[int] = None,
        lossless: bool = False,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> list[dict[str, Any]]:
        """Compress image files.

        When ``lossless`` is True the pixels are preserved exactly and only the
        encoder is optimized (PNG optimize, WEBP lossless, progressive JPEG with
        no re-quantization). Returns a list of result dicts describing the sizes.
        """
        results: list[dict[str, Any]] = []
        total = len(files)

        for i, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            if progress_callback:
                progress_callback(int((i / total) * 100))
            if progress_detail_callback:
                progress_detail_callback(
                    int((i / total) * 100),
                    f"Compressing: {Path(file_path).name}",
                )

            path = Path(file_path)
            suffix = ".webp" if lossless and path.suffix.lower() not in (".png", ".webp") else path.suffix
            output_path = path.parent / f"{path.stem}_compressed{suffix}"
            original_size = path.stat().st_size

            try:
                with Image.open(file_path) as img:
                    work = img.copy()

                if max_dimension and not lossless:
                    work = self._downscale(work, max_dimension)

                self._encode(work, output_path, quality, lossless)
                work.close()

                compressed_size = output_path.stat().st_size
                results.append(self._result(str(path), str(output_path), original_size, compressed_size))
            except Exception:
                continue

        if progress_callback:
            progress_callback(100)

        return results

    def estimate_image_compression(
        self,
        files: list[str],
        quality: int = 75,
        max_dimension: Optional[int] = None,
        lossless: bool = False,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> dict[str, Any]:
        """Estimate compressed size for images without writing output files."""
        original_total = 0
        estimated_total = 0
        per_file: list[dict[str, Any]] = []

        for file_path in files:
            if is_cancelled and is_cancelled():
                break

            path = Path(file_path)
            original_size = path.stat().st_size
            original_total += original_size

            try:
                with Image.open(file_path) as img:
                    work = img.copy()

                if max_dimension and not lossless:
                    work = self._downscale(work, max_dimension)

                buffer = io.BytesIO()
                self._encode(work, buffer, quality, lossless)
                estimated = buffer.tell()
                work.close()
            except Exception:
                estimated = original_size

            estimated_total += estimated
            per_file.append(self._result(str(path), "", original_size, estimated))

        return self._summary(original_total, estimated_total, per_file)

    def resize_images(
        self,
        files: list[str],
        mode: int = 0,
        width: int = 1920,
        height: int = 1080,
        percentage: int = 50,
        maintain_aspect: bool = True,
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> list[str]:
        """Resize images by percentage (0), dimensions (1), or max side (2)."""
        output_files: list[str] = []
        total = len(files)

        for i, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            if progress_callback:
                progress_callback(int((i / total) * 100))

            path = Path(file_path)
            output_path = path.parent / f"{path.stem}_resized{path.suffix}"

            try:
                img = Image.open(file_path)
                orig_w, orig_h = img.size

                if mode == 0:
                    scale = percentage / 100.0
                    new_size = (int(orig_w * scale), int(orig_h * scale))
                elif mode == 1:
                    if maintain_aspect:
                        ratio = min(width / orig_w, height / orig_h)
                        new_size = (int(orig_w * ratio), int(orig_h * ratio))
                    else:
                        new_size = (width, height)
                elif mode == 2:
                    max_side = max(width, height)
                    if max(orig_w, orig_h) > max_side:
                        ratio = max_side / max(orig_w, orig_h)
                        new_size = (int(orig_w * ratio), int(orig_h * ratio))
                    else:
                        new_size = (orig_w, orig_h)
                else:
                    new_size = (orig_w, orig_h)

                resized = img.resize(new_size, Image.Resampling.LANCZOS)
                if path.suffix.lower() in (".jpg", ".jpeg"):
                    resized = self._flatten_to_rgb(resized)
                    resized.save(str(output_path), "JPEG", quality=95)
                else:
                    resized.save(str(output_path))

                img.close()
                resized.close()
                output_files.append(str(output_path))
            except Exception:
                continue

        if progress_callback:
            progress_callback(100)

        return output_files

    def convert_format(
        self,
        files: list[str],
        target_format: str = "png",
        progress_callback: Optional[Callable[[int], None]] = None,
        progress_detail_callback: Optional[Callable[[int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> list[str]:
        """Convert images to a different format."""
        output_files: list[str] = []
        total = len(files)

        for i, file_path in enumerate(files):
            if is_cancelled and is_cancelled():
                break

            if progress_callback:
                progress_callback(int((i / total) * 100))

            path = Path(file_path)
            output_path = path.parent / f"{path.stem}.{target_format}"

            try:
                img = Image.open(file_path)
                save_format = "JPEG" if target_format.lower() in ("jpg", "jpeg") else target_format.upper()
                if save_format == "JPEG":
                    img = self._flatten_to_rgb(img)
                img.save(str(output_path), save_format, quality=95)
                img.close()
                output_files.append(str(output_path))
            except Exception:
                continue

        if progress_callback:
            progress_callback(100)

        return output_files

    @staticmethod
    def _downscale(img: Image.Image, max_dimension: int) -> Image.Image:
        """Downscale an image so its largest side is at most ``max_dimension``."""
        w, h = img.size
        if max(w, h) > max_dimension:
            ratio = max_dimension / max(w, h)
            return img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        return img

    @staticmethod
    def _flatten_to_rgb(img: Image.Image) -> Image.Image:
        """Flatten transparency onto a white background for RGB-only formats."""
        if img.mode in ("RGBA", "LA", "P"):
            rgba = img.convert("RGBA")
            bg = Image.new("RGB", rgba.size, (255, 255, 255))
            bg.paste(rgba, mask=rgba.split()[3])
            return bg
        if img.mode != "RGB":
            return img.convert("RGB")
        return img

    def _encode(self, img: Image.Image, target, quality: int, lossless: bool) -> None:
        """Encode an image to ``target`` (path or file-like object)."""
        fmt = getattr(target, "suffix", None)
        ext = fmt.lower() if fmt else (".webp" if lossless else ".jpg")

        if ext == ".png" or (lossless and ext not in (".jpg", ".jpeg", ".webp")):
            img.save(target, "PNG", optimize=True)
        elif ext == ".webp":
            if lossless:
                img.save(target, "WEBP", lossless=True, quality=100, method=6)
            else:
                img.save(target, "WEBP", quality=quality, method=6)
        elif ext in (".jpg", ".jpeg"):
            flat = self._flatten_to_rgb(img)
            save_quality = 95 if lossless else quality
            flat.save(target, "JPEG", quality=save_quality, optimize=True, progressive=True)
        else:
            img.save(target, "PNG", optimize=True)

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
