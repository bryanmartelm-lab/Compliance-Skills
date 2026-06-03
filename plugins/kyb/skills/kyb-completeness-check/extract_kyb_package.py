"""
KYB Package Extractor — handles duplicate filenames in zip archives.

Usage:
    python extract_kyb_package.py <zip_path> <output_dir>

Example:
    python extract_kyb_package.py kyb_package.zip ./kyb_extracted

What it does:
    1. Scans the zip for duplicate filenames
    2. Renames collisions by appending _0, _1, _2 etc.
    3. Extracts ALL files (nothing is lost)
    4. Prints a manifest of all extracted files with sizes
    5. Warns about any duplicates found
"""

import zipfile
import os
import sys
from pathlib import Path
from collections import Counter


def extract_kyb_package(zip_path: str, output_dir: str) -> dict:
    """
    Extract a KYB zip package, handling duplicate filenames.

    Returns a dict with:
        - files: list of extracted file paths
        - duplicates: list of filenames that had collisions
        - warnings: list of warning messages
    """
    zip_path = Path(zip_path)
    output_dir = Path(output_dir)

    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "files": [],
        "duplicates": [],
        "warnings": []
    }

    with zipfile.ZipFile(zip_path, 'r') as zf:
        entries = zf.infolist()

        # Skip directories
        file_entries = [e for e in entries if not e.is_dir()]

        # Detect duplicates
        name_counts = Counter(e.filename for e in file_entries)
        duplicate_names = {name for name, count in name_counts.items() if count > 1}

        if duplicate_names:
            for name in duplicate_names:
                count = name_counts[name]
                result["duplicates"].append(name)
                result["warnings"].append(
                    f"DUPLICATE: '{name}' appears {count} times in zip — "
                    f"files will be renamed with _0, _1, ... suffixes"
                )

        # Track how many times we've seen each filename
        seen_counts = {}

        for entry in file_entries:
            filename = entry.filename

            if filename in duplicate_names:
                # This filename has duplicates — rename with index
                idx = seen_counts.get(filename, 0)
                seen_counts[filename] = idx + 1

                # Split path and add suffix before extension
                path = Path(filename)
                new_name = f"{path.stem}_{idx}{path.suffix}"
                new_path = path.parent / new_name
                out_path = output_dir / new_path
            else:
                out_path = output_dir / filename

            # Create parent directories
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract file content and write.
            # For duplicates, read by position (zf.open(entry)), not by name
            # (reading by name always returns the last entry).
            with zf.open(entry) as src:
                data = src.read()

            with open(out_path, 'wb') as f:
                f.write(data)

            size_kb = len(data) / 1024
            result["files"].append({
                "original_name": filename,
                "extracted_to": str(out_path),
                "size_kb": round(size_kb, 1),
                "was_duplicate": filename in duplicate_names
            })

    return result


def print_manifest(result: dict):
    """Print a human-readable manifest of extracted files."""
    print("=" * 70)
    print("KYB PACKAGE EXTRACTION MANIFEST")
    print("=" * 70)

    # Warnings first
    if result["warnings"]:
        print("\n[!] WARNINGS:")
        for w in result["warnings"]:
            print(f"  {w}")
        print()

    # File list
    print(f"Extracted {len(result['files'])} files:\n")
    for f in result["files"]:
        dup_flag = " [!] RENAMED (duplicate)" if f["was_duplicate"] else ""
        print(f"  {f['extracted_to']}")
        print(f"    Size: {f['size_kb']} KB | Original: {f['original_name']}{dup_flag}")

    # Summary
    print(f"\n{'=' * 70}")
    total = len(result["files"])
    dups = len(result["duplicates"])
    print(f"Total files: {total} | Duplicates resolved: {dups}")
    if dups == 0:
        print("[OK] No duplicate filenames detected")
    else:
        print(f"[!] {dups} duplicate filename(s) were renamed to preserve all files")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <zip_path> <output_dir>")
        sys.exit(1)

    zip_path = sys.argv[1]
    output_dir = sys.argv[2]

    result = extract_kyb_package(zip_path, output_dir)
    print_manifest(result)
