#!/usr/bin/env python3
"""
reChronos - Reconstructing Time Through Files 
(a metadata-aware file renamer that resurrects the true timeline of your files)
Interactive CLI to recursively preview, rename, and rollback files in a directory.
- Rename format: EXT_YYMMDD_HHMMAMPM.ext
- Recursive (includes subfolders)
- Logs renames into rename_log.csv inside the given path

Version 0.9.2
Author: NMINHDUCIT
License: MIT
"""

from __future__ import annotations
import os
import sys
import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
from colorama import init as colorama_init, Fore, Style

# Initialize colorama for cross-platform colored output
colorama_init(autoreset=True)

class AnsiFore:
    GRAY = "\033[90m"
    RESET = "\033[0m"

# ---------------------------
# Utility helpers
# ---------------------------
def banner() -> None:
    """Print ASCII banner + credits & usage hint in color."""
    print(Fore.CYAN + "                 .d8888b.  888                                                 ")
    print(Fore.CYAN + "                d88P  Y88b 888                                                 ")
    print(Fore.CYAN + "                888    888 888                                                 ")
    print(Fore.CYAN + "888d888 .d88b.  888        88888b.  888d888 .d88b.  88888b.   .d88b.  .d8888b  ")
    print(Fore.CYAN + "888P'  d8P  Y8b 888        888 '88b 888P'  d88''88b 888 '88b d88''88b 88K      ")
    print(Fore.CYAN + "888    88888888 888    888 888  888 888    888  888 888  888 888  888 'Y8888b. ")
    print(Fore.CYAN + "888    Y8b.     Y88b  d88P 888  888 888    Y88..88P 888  888 Y88..88P      X88 ")
    print(Fore.CYAN + "888     'Y8888   'Y8888P'  888  888 888     'Y88P'  888  888  'Y88P'   88888P' v0.9.2")
    print()
    print(AnsiFore.GRAY + "reChronos v0.9.2 - The Metadata-aware File Renamer ( preview | rename | rollback )")
    print(AnsiFore.GRAY + "Author: Duc Nguyen | GitHub: github.com/nminhducit/reChronos")
    print(Fore.YELLOW + "Type 'help' to see available commands.")
    print()


# ---------------------------
# Core helpers
# ---------------------------
def human_ampm(dt: datetime) -> str:
    """
    Format datetime to YYMMDD_HHMMAMPM (e.g. 250930_1130PM).
    
    Args:
        dt: datetime object to format
    Returns:
        Formatted string in YYMMDD_HHMMAMPM format
    """
    date_part = dt.strftime("%y%m%d")
    time_part = dt.strftime("%I%M%p")
    return f"{date_part}_{time_part}"


def get_file_datetime(path: Path) -> datetime:
    """
    Get the OLDEST datetime for the file (closest to when photo was taken).
    Compares creation time and modification time, returns the earlier one.
    
    Args:
        path: Path object of the file
    Returns:
        datetime object of the oldest timestamp
    """
    stat = path.stat()
    
    # Get modification time
    mtime = stat.st_mtime
    
    # Get creation time (platform dependent)
    # On Windows: st_ctime is creation time
    # On Unix/Mac: try st_birthtime first, fallback to st_ctime
    if sys.platform.startswith("win"):
        ctime = stat.st_ctime
    else:
        ctime = getattr(stat, 'st_birthtime', stat.st_ctime)
    
    # Return the OLDEST time (minimum of creation and modification)
    oldest_timestamp = min(ctime, mtime)
    return datetime.fromtimestamp(oldest_timestamp)


def make_new_name(original: Path, dt: datetime, existing_names: set) -> Path:
    """
    Build a new name like EXT_YYMMDD_HHMMAMPM.ext ensuring no collision.
    If collision occurs, append _1, _2, etc.
    
    Args:
        original: Original file path
        dt: datetime to use for naming
        existing_names: Set of already used names to avoid collision
    Returns:
        Path object with new filename
    """
    # Extract extension (without dot) or use 'FILE' if no extension
    ext = original.suffix[1:] if original.suffix else ""
    prefix = ext.upper() if ext else "FILE"
    
    # Use lowercase extension for final filename
    final_ext = f".{ext.lower()}" if ext else ""
    
    # Build base name
    base = f"{prefix}_{human_ampm(dt)}"
    candidate = base + final_ext
    
    # Handle collision: append _1, _2, _3... until unique name found
    i = 1
    while candidate in existing_names:
        candidate = f"{base}_{i}{final_ext}"
        i += 1
    
    # Reserve this name in the set
    existing_names.add(candidate)
    return Path(candidate)


def gather_files_recursive(root: Path) -> List[Path]:
    """
    Recursively gather all files under root directory.
    Excludes the log file itself to avoid renaming it.
    
    Args:
        root: Root directory path
    Returns:
        List of file paths
    """
    log_name = "rename_log.csv"
    # Use rglob("*") to recursively find all files
    # Filter: only files (not dirs) and not the log file
    return [p for p in root.rglob("*") if p.is_file() and p.name != log_name]


def ensure_dir_exists(p: Path) -> None:
    """
    Ensure parent directory exists, create if necessary.
    
    Args:
        p: Path whose parent should exist
    """
    # Check if path doesn't exist, then create with parents
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)


# ---------------------------
# Core rename operations
# ---------------------------
def build_rename_plan(root: Path) -> List[Tuple[Path, Path]]:
    """
    Build complete rename plan for all files under root.
    
    Args:
        root: Root directory to scan
    Returns:
        List of tuples (old_path, new_path)
    """
    files = gather_files_recursive(root)
    plan: List[Tuple[Path, Path]] = []
    
    # Track existing names per directory to avoid collisions
    existing_by_dir: Dict[Path, set] = defaultdict(set)

    # Loop through each file and generate new name
    for file_path in files:
        parent_dir = file_path.parent
        
        # Initialize set of existing names for this directory if not done
        if parent_dir not in existing_by_dir:
            # Get all current filenames in this directory
            existing_by_dir[parent_dir] = {p.name for p in parent_dir.iterdir() if p.is_file()}
        
        # Get file datetime and generate new name
        dt = get_file_datetime(file_path)
        new_name = make_new_name(file_path, dt, existing_by_dir[parent_dir])
        new_full = parent_dir / new_name
        
        # Add to plan
        plan.append((file_path, new_full))
    
    return plan


def preview_plan(plan: List[Tuple[Path, Path]], max_show: int = 10) -> None:
    """
    Display preview of rename plan with summary.
    
    Args:
        plan: List of (old, new) path tuples
        max_show: Maximum number of files to display
    """
    total = len(plan)
    
    # Show first N planned renames
    for i, (old_path, new_path) in enumerate(plan[:max_show], start=1):
        print(f"{i}. {old_path.name} → {Fore.GREEN}{new_path.name}{Style.RESET_ALL}")
    
    # If more files than shown, print summary
    if total > max_show:
        print(f"... and {total - max_show} more files")
    
    print(f"Total files planned: {total}\n")


def append_log_csv(log_path: Path, rows: List[List[str]]) -> None:
    """
    Append operations to CSV log file with UTF-8 encoding.
    Creates file with header if it doesn't exist.
    
    Args:
        log_path: Path to log CSV file
        rows: List of rows to append [batch_id, timestamp, src, dst, action]
    """
    header = ["batch_id", "timestamp", "src", "dst", "action"]
    exists = log_path.exists()
    
    # Ensure parent directory exists
    ensure_dir_exists(log_path.parent)
    
    # Open in append mode with UTF-8-BOM for Excel compatibility
    with log_path.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        
        # Write header if file is new
        if not exists:
            writer.writerow(header)
        
        # Write all rows
        writer.writerows(rows)


def perform_rename(root: Path, plan: List[Tuple[Path, Path]]) -> None:
    """
    Execute rename operations and log to CSV.
    Each execution gets a unique batch_id for rollback tracking.
    
    Args:
        root: Root directory (where log will be saved)
        plan: List of (src, dst) path tuples to rename
    """
    # Generate unique batch ID using timestamp
    batch_id = datetime.now().strftime("%Y%m%d%H%M%S")
    timestamp = datetime.now().isoformat()
    log_path = root / "rename_log.csv"
    rows = []

    # Process each planned rename
    for src, dst in plan:
        # Check if source file still exists
        if not src.exists():
            rows.append([batch_id, timestamp, str(src.resolve()), str(dst.resolve()), "skip_missing_src"])
            print(Fore.YELLOW + f"Skipped missing source: {src}")
            continue

        target_dst = dst
        
        # Handle collision: if destination exists and is different file
        if target_dst.exists() and target_dst.resolve() != src.resolve():
            base = target_dst.stem
            ext = target_dst.suffix
            i = 1
            
            # Find non-conflicting name by appending _1, _2...
            while True:
                new_candidate = target_dst.with_name(f"{base}_{i}{ext}")
                # Break when unique name found
                if not new_candidate.exists():
                    target_dst = new_candidate
                    break
                i += 1
            
            print(Fore.YELLOW + f"Conflict: {dst.name} exists — renaming to {target_dst.name}")

        # Ensure destination directory exists
        ensure_dir_exists(target_dst.parent)

        # Attempt to move/rename file
        try:
            shutil.move(str(src), str(target_dst))
            # Log successful rename with absolute paths
            rows.append([batch_id, timestamp, str(src.resolve()), str(target_dst.resolve()), "rename"])
            print(f"  {src.name} → {Fore.GREEN}{target_dst.name}{Style.RESET_ALL}")
        except Exception as e:
            # Log error if rename fails
            rows.append([batch_id, timestamp, str(src.resolve()), str(target_dst.resolve()), f"error:{e}"])
            print(Fore.RED + f"Error renaming {src.name}: {e}")

    # Save all operations to log
    append_log_csv(log_path, rows)
    
    # Count successful renames
    success_count = len([r for r in rows if r[4] == 'rename'])
    print(Fore.CYAN + f"\nBatch {batch_id} completed: {success_count} files renamed")
    print(Fore.CYAN + f"Log saved to {log_path}\n")


def read_log_csv(log_path: Path) -> List[Dict[str, str]]:
    """
    Read entire CSV log into list of dictionaries.
    
    Args:
        log_path: Path to log file
    Returns:
        List of dict rows with header as keys
    """
    # Return empty list if log doesn't exist
    if not log_path.exists():
        return []
    
    # Read CSV with UTF-8-BOM encoding
    with log_path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def find_last_batch(log_rows: List[Dict[str, str]]) -> str | None:
    """
    Find the most recent batch_id with actual rename actions.
    
    Args:
        log_rows: List of log entries
    Returns:
        Last batch_id or None if no batches found
    """
    # Return None if no log entries
    if not log_rows:
        return None
    
    # Search from end to find last rename batch
    batch_ids = []
    for row in reversed(log_rows):
        action = row.get("action", "")
        batch_id = row.get("batch_id", "")
        
        # Only consider rename actions (not rollback)
        # Add batch_id if not already in list
        if action == "rename" and batch_id and batch_id not in batch_ids:
            batch_ids.append(batch_id)
    
    # Return first (most recent) batch or None
    return batch_ids[0] if batch_ids else None


def rollback_last_batch(root: Path) -> None:
    """
    Rollback the last batch of renames.
    Processes operations in reverse order to minimize conflicts.
    
    Args:
        root: Root directory containing rename_log.csv
    """
    log_path = root / "rename_log.csv"
    rows = read_log_csv(log_path)
    
    # Check if log exists
    if not rows:
        print(Fore.YELLOW + "No log found to rollback.\n")
        return
    
    # Find last batch ID
    last_batch = find_last_batch(rows)
    if not last_batch:
        print(Fore.YELLOW + "No batch id found in log.\n")
        return

    # Filter rows: only this batch and only rename actions
    batch_rows = [r for r in rows if r.get("batch_id") == last_batch and r.get("action") == "rename"]
    
    # Check if batch has any rename operations
    if not batch_rows:
        print(Fore.YELLOW + "No rename entries found for the last batch.\n")
        return
    
    print(Fore.CYAN + f"Rolling back batch {last_batch} ({len(batch_rows)} files)...\n")
    
    rollback_actions = []
    success_count = 0
    
    # Process in reverse order (last renamed first)
    for entry in reversed(batch_rows):
        src_str = entry.get("src", "")
        dst_str = entry.get("dst", "")
        
        # Convert string paths back to Path objects
        src = Path(src_str)
        dst = Path(dst_str)
        
        # Check if renamed file (destination) still exists
        if not dst.exists():
            rollback_actions.append([last_batch, datetime.now().isoformat(), dst_str, src_str, "rollback_missing_dst"])
            print(Fore.YELLOW + f"Cannot rollback {dst.name}: file not found")
            continue

        final_src = src
        
        # Check if original path is now occupied by another file
        if final_src.exists():
            base, ext = src.stem, src.suffix
            i = 1
            
            # Find alternative name: original_restored_1, _2, etc.
            while True:
                candidate = src.with_name(f"{base}_restored_{i}{ext}")
                # Break when unique name found
                if not candidate.exists():
                    final_src = candidate
                    break
                i += 1
            
            print(Fore.YELLOW + f"Original path occupied — restoring to {final_src.name}")

        # Attempt to move file back to original (or alternative) name
        try:
            shutil.move(str(dst), str(final_src))
            rollback_actions.append([last_batch, datetime.now().isoformat(), dst_str, str(final_src.resolve()), "rollback"])
            print(Fore.GREEN + f"✓ Rolled back: {dst.name} → {final_src.name}")
            success_count += 1
        except Exception as e:
            rollback_actions.append([last_batch, datetime.now().isoformat(), dst_str, str(final_src.resolve()), f"rollback_failed:{e}"])
            print(Fore.RED + f"✗ Failed to rollback {dst.name}: {e}")

    # Log all rollback operations
    append_log_csv(log_path, rollback_actions)
    print(Fore.CYAN + f"\nRollback complete: {success_count}/{len(batch_rows)} files restored")
    print(Fore.CYAN + f"Rollback logged to {log_path}\n")


# ---------------------------
# Interactive CLI
# ---------------------------
def print_help() -> None:
    """Print available commands and usage information."""
    print("Available commands:")
    print("  preview [path]   - Show rename plan for path (default: current dir).")
    print("  rename [path]    - Execute rename on directory (default: current dir).")
    print("  rollback [path]  - Rollback last rename batch (default: current dir).")
    print("  help             - Show this help.")
    print("  quit / exit      - Exit the program.")
    print()
    print("Notes:")
    print(" - Supports folders with Vietnamese and Unicode characters")
    print(" - Uses oldest date (created or modified) for rename")
    print(" - Creates 'rename_log.csv' inside target directory")
    print(" - Renames files recursively (includes subfolders)")
    print()


def interactive_loop() -> None:
    """Main interactive command loop."""
    banner()
    
    # Main loop: read and process commands until quit
    while True:
        try:
            cmdline = input(Fore.BLUE + "reChronos@root# " + Style.RESET_ALL).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        # Skip empty input
        if not cmdline:
            continue

        # Parse command and arguments
        parts = cmdline.split(maxsplit=1)
        cmd = parts[0].lower()
        
        # Handle quoted paths properly
        if len(parts) > 1:
            arg_str = parts[1].strip()
            # Remove surrounding quotes if present
            if (arg_str.startswith('"') and arg_str.endswith('"')) or \
               (arg_str.startswith("'") and arg_str.endswith("'")):
                arg_str = arg_str[1:-1]
            args = [arg_str] if arg_str else []
        else:
            args = []

        # Command: preview rename plan
        if cmd == "preview":
            # Use provided path or current directory
            target = Path(args[0]).expanduser().resolve() if args else Path.cwd()
            
            # Validate directory exists
            if not target.exists() or not target.is_dir():
                print(Fore.RED + f"Invalid directory: {target}")
                continue
            
            # Build and show plan
            plan = build_rename_plan(target)
            preview_plan(plan, max_show=10)
            continue

        # Command: execute rename
        if cmd == "rename":
            # Use provided path or current directory
            target = Path(args[0]).expanduser().resolve() if args else Path.cwd()
            
            # Validate directory exists
            if not target.is_dir():
                print(Fore.RED + f"Invalid directory: {target}")
                continue
            
            # Build plan
            plan = build_rename_plan(target)
            
            # Check if any files to rename
            if not plan:
                print(Fore.YELLOW + "No files to rename.\n")
                continue
            
            # Show preview
            preview_plan(plan)
            
            # Ask for confirmation
            confirm = input(Fore.MAGENTA + "Proceed with rename? (yes/no): " + Style.RESET_ALL).strip().lower()
            
            # Execute if confirmed
            if confirm in ("y", "yes"):
                perform_rename(target, plan)
            else:
                print(Fore.CYAN + "Rename canceled by user.\n")
            continue

        # Command: rollback last batch
        if cmd == "rollback":
            # Use provided path or current directory
            target = Path(args[0]).expanduser().resolve() if args else Path.cwd()
            
            # Validate directory exists
            if not target.exists() or not target.is_dir():
                print(Fore.RED + f"Invalid directory: {target}")
                continue
            
            # Ask for confirmation
            confirm = input(Fore.MAGENTA + f"Rollback last batch in {target}? (yes/no): " + Style.RESET_ALL).strip().lower()
            
            # Execute if confirmed
            if confirm in ("y", "yes"):
                rollback_last_batch(target)
            else:
                print(Fore.CYAN + "Rollback canceled.\n")
            continue

        # Command: show help
        if cmd == "help":
            print_help()
            continue

        # Command: quit program
        if cmd in ("quit", "exit"):
            print("Goodbye.")
            break

        # Unknown command
        print(Fore.RED + f"Unknown command: {cmd}. Type 'help' to see available commands.")


if __name__ == "__main__":
    interactive_loop()