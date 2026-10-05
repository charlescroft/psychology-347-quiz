#!/usr/bin/env python3
"""CLI entrypoint for the Scanned PDF Compressor."""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from pdf_compressor import (
    PDFCompressor,
    CompressionConfig,
    format_size,
    get_pdf_info,
    find_latest_large_pdf,
)

PRESETS = {
    "ocr": {"dpi": 200, "quality": 80, "grayscale": False, "desc": "Standard OCR (200 DPI, Q=80, Color) [Recommended]"},
    "ocr-hq": {"dpi": 300, "quality": 85, "grayscale": False, "desc": "High Fidelity OCR (300 DPI, Q=85, Color)"},
    "ocr-gray": {"dpi": 200, "quality": 80, "grayscale": True, "desc": "Grayscale OCR (200 DPI, Q=80, Grayscale, Smaller size)"},
    "compact": {"dpi": 150, "quality": 75, "grayscale": True, "desc": "Compact (150 DPI, Q=75, Grayscale, Minimal size)"},
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="High-performance PDF Compressor for large scanned homework/documents, optimized for OCR."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to input PDF file. If omitted, automatically searches for the latest large PDF in ~/Downloads.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Path to output compressed PDF. Defaults to '<input_name>_compressed.pdf'.",
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        default="ocr",
        help="Compression preset profile. Default is 'ocr'.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=None,
        help="Target DPI (e.g. 150, 200, 300). Overrides preset DPI.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=None,
        help="JPEG quality (1-100). Overrides preset quality.",
    )
    parser.add_argument(
        "--grayscale",
        action="store_true",
        default=None,
        help="Convert pages to grayscale (saves ~30-50%% space).",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="Number of parallel worker processes. Default: all available CPU cores.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show detailed information about the input PDF without compressing.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine input file
    input_file: Optional[str] = args.input
    if not input_file:
        print("[*] No input PDF specified, scanning ~/Downloads for latest large PDF...")
        candidate = find_latest_large_pdf(directory="~/Downloads", min_size_mb=10.0)
        if candidate:
            print(f"[+] Found candidate PDF: {candidate}")
            input_file = candidate
        else:
            print("[-] No large PDF found in ~/Downloads. Please provide a file path explicitly.")
            sys.exit(1)

    in_path = Path(input_file).expanduser().resolve()
    if not in_path.exists():
        print(f"[-] Error: Input file does not exist: {in_path}")
        sys.exit(1)

    # Print input info
    info = get_pdf_info(str(in_path))
    print(f"[*] Input: {info['filename']}")
    print(f"[*] Size:  {info['size_formatted']} ({info['size_bytes']:,} bytes)")
    print(f"[*] Pages: {info['page_count']}")

    if args.info:
        sys.exit(0)

    # Resolve preset and overrides
    preset_cfg = PRESETS[args.preset]
    dpi = args.dpi if args.dpi is not None else preset_cfg["dpi"]
    quality = args.quality if args.quality is not None else preset_cfg["quality"]
    grayscale = args.grayscale if args.grayscale is not None else preset_cfg["grayscale"]

    config = CompressionConfig(
        dpi=dpi,
        quality=quality,
        grayscale=grayscale,
        workers=args.workers or (CompressionConfig.workers),
    )

    print(f"[*] Preset: {args.preset} ({preset_cfg['desc']})")
    print(f"[*] Settings: DPI={config.dpi}, Quality={config.quality}, Grayscale={config.grayscale}, Workers={config.workers}")

    # Set up progress reporting
    total_pages = info["page_count"]
    pbar = None
    if tqdm:
        pbar = tqdm(total=total_pages, desc="Compressing pages", unit="page")

        def on_progress(completed: int, total: int):
            pbar.update(1)
    else:
        last_reported = 0

        def on_progress(completed: int, total: int):
            nonlocal last_reported
            percent = (completed / total) * 100.0
            if completed == total or (completed - last_reported) >= max(1, total // 10):
                print(f"[*] Progress: {completed}/{total} pages ({percent:.1f}%)")
                last_reported = completed

    compressor = PDFCompressor(config=config)

    try:
        result = compressor.compress(
            input_path=str(in_path),
            output_path=args.output,
            progress_callback=on_progress,
        )
    finally:
        if pbar:
            pbar.close()

    print("\n" + result.summary())


if __name__ == "__main__":
    main()
