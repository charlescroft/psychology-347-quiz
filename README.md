# Scanned PDF Compressor (for OCR Preprocessing)

A high-performance Python tool designed to compress excessively large scanned PDFs (such as multi-gigabyte student homework scans or lecture notes) into lightweight, clean documents optimized for OCR recognition (Tesseract, Apple Vision, PaddleOCR, Adobe Acrobat, etc.).

## Features

- **Multi-Process Parallel Acceleration:** Uses all available CPU cores to process and compress pages simultaneously.
- **OCR-Optimized Rendering:** Resolves 10k+ dpi oversized scans, complex vector artifacts, and overlapping sticker layers into clean, high-contrast, uniformly scaled pages at 200–300 DPI.
- **Clean Document Slate:** Eliminates stray garbled scanner recognition artifacts that can confuse downstream OCR engines.
- **Preset Profiles:** Easily switch between `ocr` (recommended), `ocr-hq`, `ocr-gray`, and `compact`.
- **Auto-Discovery:** Automatically detects the newest large PDF in `~/Downloads` if no input path is specified.

## Installation & Setup

A dedicated virtual environment has been created at `/Volumes/Ext/dev/python/pdf_compressor/.venv`.

Dependencies:
- `pymupdf` (PDF rendering & extraction)
- `pillow` (image processing)
- `tqdm` (progress bar)

To install or reinstall:
```bash
cd /Volumes/Ext/dev/python/pdf_compressor
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

### 1. Compress the student's homework directly:
```bash
/Volumes/Ext/dev/python/pdf_compressor/run.sh
```
*If no file is passed, it automatically locates the latest large PDF in `~/Downloads` (`心理学导论-162.pdf`) and produces `心理学导论-162_compressed.pdf`.*

### 2. Specify input and output paths:
```bash
/Volumes/Ext/dev/python/pdf_compressor/run.sh /path/to/input.pdf -o /path/to/output.pdf
```

### 3. Presets:
- **`ocr` (Default):** 200 DPI, JPEG Quality 80, Full Color. Preserves colored pens and highlighter marks while cutting file size by 95%+.
  ```bash
  ./run.sh input.pdf --preset ocr
  ```
- **`ocr-gray`:** 200 DPI, JPEG Quality 80, Grayscale. Ideal for pure black/white text homework; further shrinks file size.
  ```bash
  ./run.sh input.pdf --preset ocr-gray
  ```
- **`ocr-hq`:** 300 DPI, JPEG Quality 85, Full Color. Maximum fidelity for small fonts or intricate handwriting.
  ```bash
  ./run.sh input.pdf --preset ocr-hq
  ```
- **`compact`:** 150 DPI, JPEG Quality 75, Grayscale. Maximum compression for quick mobile reading.
  ```bash
  ./run.sh input.pdf --preset compact
  ```

### 4. Custom Parameter Tuning:
```bash
./run.sh input.pdf --dpi 220 -q 82 --workers 8
```
