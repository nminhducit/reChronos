import argparse
import csv
from datetime import datetime
from pathlib import Path
import os
from PIL import Image
import piexif
import shutil

# ====== Các định dạng ảnh được hỗ trợ ======
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff")

# ====== Hàm lấy timestamp chính xác nhất ======
def get_best_timestamp(file_path: Path) -> datetime:
    """
    Lấy timestamp chính xác nhất theo thứ tự ưu tiên:
    1. Nếu có EXIF:
       - Nếu Date Modified cũ hơn cả EXIF và Date Created → ưu tiên Date Modified
       - Ngược lại → dùng EXIF DateTimeOriginal
    2. Nếu không có EXIF → lấy timestamp cũ nhất giữa Date Modified và Date Created
    """
    try:
        # 1. Lấy timestamp từ filesystem
        stat = file_path.stat()
        mod_time = datetime.fromtimestamp(stat.st_mtime)   # Date Modified
        create_time = datetime.fromtimestamp(stat.st_ctime) # Date Created (Windows)

        # 2. Đọc EXIF DateTimeOriginal
        exif_time = None
        try:
            img = Image.open(file_path)
            exif_data = img.info.get("exif")
            if exif_data:
                exif_dict = piexif.load(exif_data)

                # Lấy EXIF DateTimeOriginal hoặc DateTimeDigitized
                dto = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
                if not dto:
                    dto = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeDigitized)
                if not dto:
                    dto = exif_dict["0th"].get(piexif.ImageIFD.DateTime)

                if dto:
                    exif_time = datetime.strptime(dto.decode("utf-8"), "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass  # Không có EXIF hoặc lỗi đọc EXIF

        # 3. Logic chọn timestamp
        if exif_time:
            if mod_time < exif_time and mod_time < create_time:
                return mod_time
            return exif_time
        else:
            return min(mod_time, create_time)

    except Exception as e:
        print(f"[WARNING] Không thể lấy timestamp cho {file_path}: {e}")
        return datetime.fromtimestamp(file_path.stat().st_mtime)

# ====== Hàm format tên file ======
def format_new_name(timestamp: datetime, ext: str, index: int = None):
    """
    Định dạng tên file theo yêu cầu:
    IMG_250929_1103AM.jpg
    """
    date_part = timestamp.strftime("%d%m%y")   # ddmmyy
    time_part = timestamp.strftime("%I%M%p")   # 12h + AM/PM
    new_name = f"IMG_{date_part}_{time_part}{ext.lower()}"
    if index:
        new_name = f"IMG_{date_part}_{time_part}_{index}{ext.lower()}"
    return new_name

# ====== Hàm đổi tên file ======
def rename_images_in_dir(target_dir: Path, recursive=False, dry_run=False, log_path=None):
    files = []
    if recursive:
        files = [f for f in target_dir.rglob("*") if f.suffix.lower() in IMAGE_EXTENSIONS]
    else:
        files = [f for f in target_dir.glob("*") if f.suffix.lower() in IMAGE_EXTENSIONS]

    if not files:
        print("[INFO] Không tìm thấy file ảnh nào.")
        return

    print(f"[INFO] Tìm thấy {len(files)} file ảnh cần xử lý.\n")

    # Chuẩn bị file CSV log mapping
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not log_path:
        log_path = target_dir / f"rename_log.csv"

    with open(log_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["old_path", "new_path"])

        renamed_count = 0
        conflict_count = 0
        error_count = 0

        for file in files:
            try:
                # Lấy timestamp chuẩn
                best_time = get_best_timestamp(file)

                # Sinh tên mới
                new_name = format_new_name(best_time, file.suffix)
                new_path = file.parent / new_name
                index = 1
                while new_path.exists():
                    new_name = format_new_name(best_time, file.suffix, index)
                    new_path = file.parent / new_name
                    index += 1
                    conflict_count += 1

                if dry_run:
                    print(f"[DRY-RUN] {file} -> {new_path}")
                else:
                    file.rename(new_path)
                    print(f"[RENAME] {file.name} -> {new_path.name}")

                writer.writerow([str(file), str(new_path)])
                renamed_count += 1

            except PermissionError:
                print(f"[ERROR] Không có quyền đổi tên: {file}")
                error_count += 1
            except Exception as e:
                print(f"[ERROR] Lỗi khi xử lý {file}: {e}")
                error_count += 1

    # In báo cáo
    print("\n=== KẾT QUẢ ===")
    print(f"Tổng số file ảnh: {len(files)}")
    print(f"Đổi tên thành công: {renamed_count}")
    print(f"Trùng tên đã xử lý: {conflict_count}")
    print(f"Lỗi: {error_count}")
    print(f"Mapping lưu tại: {log_path}")
    if dry_run:
        print("[NOTE] Đây là chế độ dry-run, không có file nào bị đổi tên thực tế.")

# ====== Hàm rollback ======
def rollback_from_csv(csv_path):
    if not Path(csv_path).exists():
        print("[ERROR] File mapping không tồn tại.")
        return

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            old_path = Path(row["old_path"])
            new_path = Path(row["new_path"])
            if new_path.exists():
                try:
                    new_path.rename(old_path)
                    print(f"[ROLLBACK] {new_path.name} -> {old_path.name}")
                except Exception as e:
                    print(f"[ERROR] Rollback thất bại cho {new_path}: {e}")

# ====== Main CLI ======
def main():
    parser = argparse.ArgumentParser(description="Đổi tên file ảnh dựa trên timestamp.")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: rename
    rename_parser = subparsers.add_parser("rename", help="Đổi tên ảnh trong thư mục")
    rename_parser.add_argument("--dir", required=True, help="Thư mục chứa ảnh")
    rename_parser.add_argument("--recursive", action="store_true", help="Đệ quy vào thư mục con")
    rename_parser.add_argument("--dry-run", action="store_true", help="Chỉ xem trước, không thực hiện")
    rename_parser.add_argument("--log", help="Đường dẫn file CSV log mapping")

    # Subcommand: rollback
    rollback_parser = subparsers.add_parser("rollback", help="Phục hồi tên file từ CSV log")
    rollback_parser.add_argument("--map", required=True, help="Đường dẫn đến file mapping CSV")

    args = parser.parse_args()

    if args.command == "rename":
        target_dir = Path(args.dir)
        if not target_dir.exists():
            print("[ERROR] Thư mục không tồn tại.")
            return
        rename_images_in_dir(
            target_dir,
            recursive=args.recursive,
            dry_run=args.dry_run,
            log_path=Path(args.log) if args.log else None
        )

    elif args.command == "rollback":
        rollback_from_csv(args.map)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
