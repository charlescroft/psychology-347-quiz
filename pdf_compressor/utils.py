"""Utility helpers for PDF inspection and file handling."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import pymupdf


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:3.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """Retrieve metadata and basic statistics of a PDF file."""
    path = Path(pdf_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    file_size = path.stat().st_size
    doc = pymupdf.open(str(path))
    page_count = len(doc)

    first_page_dims = (0.0, 0.0)
    image_count_sample = 0
    if page_count > 0:
        first_page = doc[0]
        first_page_dims = (round(first_page.rect.width, 1), round(first_page.rect.height, 1))
        image_count_sample = len(first_page.get_images())
    doc.close()

    return {
        "path": str(path),
        "filename": path.name,
        "size_bytes": file_size,
        "size_formatted": format_size(file_size),
        "page_count": page_count,
        "first_page_dims": first_page_dims,
        "first_page_images": image_count_sample,
    }


def find_latest_large_pdf(directory: str = "~/Downloads", min_size_mb: float = 10.0) -> Optional[str]:
    """Find the most recently modified large PDF in the specified directory."""
    dir_path = Path(directory).expanduser().resolve()
    if not dir_path.is_dir():
        return None

    min_bytes = int(min_size_mb * 1024 * 1024)
    candidates = []

    for item in dir_path.glob("*.pdf"):
        try:
            stat = item.stat()
            if stat.st_size >= min_bytes:
                candidates.append((stat.st_mtime, item))
        except OSError:
            continue

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return str(candidates[0][1])
