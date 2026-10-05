"""Core PDF compression engine tailored for scanned documents and OCR workflows."""

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
import pymupdf

from .utils import format_size


@dataclass
class CompressionConfig:
    """Configuration options for PDF compression."""
    dpi: int = 200
    quality: int = 80
    grayscale: bool = False
    workers: int = os.cpu_count() or 4
    max_dim: Optional[int] = None


@dataclass
class CompressionResult:
    """Results and statistics from a compression run."""
    input_path: str
    output_path: str
    total_pages: int
    original_size: int
    compressed_size: int
    duration_seconds: float

    @property
    def savings_bytes(self) -> int:
        return max(0, self.original_size - self.compressed_size)

    @property
    def ratio(self) -> float:
        if self.original_size == 0:
            return 0.0
        return self.compressed_size / self.original_size

    @property
    def savings_percent(self) -> float:
        if self.original_size == 0:
            return 0.0
        return (1.0 - self.ratio) * 100.0

    @property
    def pages_per_second(self) -> float:
        if self.duration_seconds <= 0:
            return 0.0
        return self.total_pages / self.duration_seconds

    def summary(self) -> str:
        lines = [
            "--------------------------------------------------",
            "PDF Compression Summary",
            "--------------------------------------------------",
            f"Input file:       {self.input_path}",
            f"Output file:      {self.output_path}",
            f"Total pages:      {self.total_pages}",
            f"Original size:    {format_size(self.original_size)} ({self.original_size:,} bytes)",
            f"Compressed size:  {format_size(self.compressed_size)} ({self.compressed_size:,} bytes)",
            f"Space saved:      {format_size(self.savings_bytes)} ({self.savings_percent:.1f}% reduction)",
            f"Time elapsed:     {self.duration_seconds:.2f}s ({self.pages_per_second:.1f} pages/sec)",
            "--------------------------------------------------",
        ]
        return "\n".join(lines)


def _render_page_worker(args: tuple) -> tuple:
    """Worker function for rendering and compressing a single page in a separate process.

    Args:
        args: (pdf_path, page_num, dpi, quality, grayscale)
    Returns:
        (page_num, width, height, jpeg_bytes)
    """
    pdf_path, page_num, dpi, quality, grayscale = args
    doc = pymupdf.open(pdf_path)
    try:
        page = doc[page_num]
        rect = page.rect
        width, height = rect.width, rect.height

        colorspace = pymupdf.csGRAY if grayscale else pymupdf.csRGB
        pix = page.get_pixmap(dpi=dpi, colorspace=colorspace)
        jpeg_bytes = pix.tobytes("jpeg", jpg_quality=quality)
        return (page_num, width, height, jpeg_bytes)
    finally:
        doc.close()


class PDFCompressor:
    """High-performance multi-process PDF compressor for scanned documents."""

    def __init__(self, config: Optional[CompressionConfig] = None):
        self.config = config or CompressionConfig()

    def compress(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> CompressionResult:
        """Compress the specified PDF file.

        Args:
            input_path: Path to the input PDF file.
            output_path: Path to save the compressed PDF. If None, appends '_compressed.pdf'.
            progress_callback: Optional callback receiving (completed_pages, total_pages).

        Returns:
            CompressionResult with detailed stats.
        """
        in_p = Path(input_path).expanduser().resolve()
        if not in_p.exists():
            raise FileNotFoundError(f"Input PDF does not exist: {input_path}")

        if output_path is None:
            out_p = in_p.with_stem(f"{in_p.stem}_compressed")
        else:
            out_p = Path(output_path).expanduser().resolve()

        out_p.parent.mkdir(parents=True, exist_ok=True)

        original_size = in_p.stat().st_size
        start_time = time.time()

        # Open source to read page count
        src_doc = pymupdf.open(str(in_p))
        total_pages = len(src_doc)
        src_doc.close()

        if total_pages == 0:
            raise ValueError(f"PDF file has 0 pages: {input_path}")

        # Prepare arguments for multiprocessing
        tasks = [
            (
                str(in_p),
                page_idx,
                self.config.dpi,
                self.config.quality,
                self.config.grayscale,
            )
            for page_idx in range(total_pages)
        ]

        # Use ProcessPoolExecutor to render and compress pages in parallel
        max_workers = max(1, min(self.config.workers, total_pages))
        page_results: dict[int, tuple[float, float, bytes]] = {}
        completed_count = 0

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(_render_page_worker, t): t[1] for t in tasks
            }

            for future in as_completed(future_to_page):
                page_num, width, height, jpeg_bytes = future.result()
                page_results[page_num] = (width, height, jpeg_bytes)
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, total_pages)

        # Reconstruct output PDF in correct page order
        out_doc = pymupdf.open()
        for page_idx in range(total_pages):
            width, height, jpeg_bytes = page_results[page_idx]
            new_page = out_doc.new_page(width=width, height=height)
            rect = pymupdf.Rect(0, 0, width, height)
            new_page.insert_image(rect, stream=jpeg_bytes)

        # Save with full deflating and garbage collection
        out_doc.save(str(out_p), garbage=4, deflate=True)
        out_doc.close()

        duration = time.time() - start_time
        compressed_size = out_p.stat().st_size

        return CompressionResult(
            input_path=str(in_p),
            output_path=str(out_p),
            total_pages=total_pages,
            original_size=original_size,
            compressed_size=compressed_size,
            duration_seconds=duration,
        )
