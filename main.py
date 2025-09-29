#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RID (Rename Images by Date)
Author: NMINHDUCIT
GitHub: https://github.com/nminhducit

Description:
    Rename image files based on EXIF DateTimeOriginal or file timestamps.
    This helps organize photos by the actual time they were taken.
"""

import os
import sys
import csv
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}

# ==============================================================================
# Utility functions
# ==============================================================================

def print_banner():
    """Display a nice banner at program start"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
██████╗ ██╗██████╗ 
██╔══██╗██║██╔══██╗
██████╔╝██║██║  ██║
██╔═══╝ ██║██║  ██║
██║     ██║██████╔╝
╚═╝     ╚═╝╚═════╝   {Fore.YELLOW}RID - Rename Images by Date
{Style.RESET_ALL}
"""
    print(banner)


def get_exif_datetime(file_path: Path):
    """Get EXIF DateTimeOriginal from an image if available."""
    try:
        with Image.open(file_path) as img:
            exif_data = img.getexif()
            if not exif_data:
                return None

            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None
    return None


def get_file_timestamps(file_path: Path):
    """
    Get file timestamps:
      - created_time: File creation time
      - modified_time: Last modified time
    """
    stat = file_path.stat()
    created_time = datetime.fromtimestamp(stat.st_ctime)
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    return created_time, modified_time


def get_best_timestamp(file_path: Path):
    """
    Determine the best timestamp for renaming:
      Priority:
        1. EXIF DateTimeOriginal (if exists)
        2. If ModifiedTime < DateTimeOriginal or CreatedTime → use ModifiedTime
        3. Otherwise, use CreatedTime
    """
    exif_time = get_exif_datetime(file_path)
    created_time, modified_time = get_file_timestamps(file_path)

    # If EXIF exists, compare with modified_time
    if exif_time:
        if modified_time < exif_time:
            return modified_time
        return exif_time

    # If EXIF missing, choose the oldest between created and modified
    return min(created_time, modified_time)


def format_new_filename(timestamp: datetime):
    """
    Format timestamp into string:
    Example: IMG_250929_1103AM
    - 25/09/29 -> 250929
    - 11:03AM -> 1103AM
    """
    date_part = timestamp.strftime("%y%m%d")
    time_part = timestamp.strftime("%I%M%p").upper()
    return f"IMG_{date_part}_{time_part}"


def safe_rename(file_path: Path, new_name: str, dry_run=False):
    """
    Safely rename a file, avoid overwriting by adding suffix _1, _2, etc.
    """
    target_dir = file_path.parent
    ext = file_path.suffix.lower()
    candidate_name = new_name + ext
    counter = 1

    while (target_dir / candidate_name).exists():
        candidate_name = f"{new_name}_{counter}{ext}"
        counter += 1

    new_path = target_dir / candidate_name

    if not dry_run:
        file_path.rename(new_path)

    return new_path


# ==============================================================================
# Core Function
# ==============================================================================

def rename_images_in_dir(directory: Path, recursive=False, dry_run=False, log_file="rename_logs.csv"):
    """
    Rename all images in a directory based on EXIF or file timestamps.
    """
    all_files = directory.rglob("*") if recursive else directory.glob("*")
    images = [f for f in all_files if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]

    if not images:
        print(Fore.RED + "No image files found.")
        return

    # Prepare CSV logging
    log_path = directory / f"rename_logs.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original Path", "New Path", "Timestamp Used"])

        print(Fore.GREEN + f"\n[Processing] Found {len(images)} images to rename...\n")

        count = 0
        for file in images:
            timestamp = get_best_timestamp(file)
            if not timestamp:
                print(Fore.YELLOW + f"[SKIP] Cannot determine timestamp for: {file}")
                continue

            new_name = format_new_filename(timestamp)
            new_path = safe_rename(file, new_name, dry_run=dry_run)

            writer.writerow([str(file), str(new_path), timestamp.strftime("%Y-%m-%d %H:%M:%S")])

            if dry_run:
                print(Fore.CYAN + f"[DRY-RUN] {file.name} -> {new_path.name}")
            else:
                print(Fore.GREEN + f"[RENAME] {file.name} -> {new_path.name}")
            count += 1

    print(Fore.BLUE + "\n=== Summary ===")
    print(Fore.WHITE + f"Total images processed: {len(images)}")
    print(Fore.WHITE + f"Successfully renamed: {count}")
    print(Fore.WHITE + f"Log saved at: {log_path}")
    print(Fore.GREEN + "Operation completed.\n")


# ==============================================================================
# Main CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="RID - Rename Images by Date\nCredit: NMINHDUCIT",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "rename",
        help="Action to perform (currently only supports 'rename')"
    )
    parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="Target directory containing images"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for images in subdirectories recursively"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually renaming files"
    )

    args = parser.parse_args()

    print_banner()

    target_dir = Path(args.dir).resolve()
    if not target_dir.exists():
        print(Fore.RED + f"Error: Directory does not exist: {target_dir}")
        sys.exit(1)

    if args.rename.lower() == "rename":
        rename_images_in_dir(
            target_dir,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
    else:
        print(Fore.RED + "Invalid action. Only 'rename' is supported.")
        sys.exit(1)


if __name__ == "__main__":
    main()
