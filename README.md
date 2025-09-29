# 🖼️ RID command (Rename Images by Date)

A Python script to **rename image files based on their actual creation date**, determined by EXIF metadata or the file's timestamp (`Date Created`, `Date Modified`).  
Perfect for organizing personal photos, backups, or standardizing image file names for better sorting and management.

---
## 🚀 Features

- **Rename images based on the most accurate timestamp:**
  1. Prioritizes `EXIF DateTimeOriginal` if available.
  2. If `Date Modified` is **earlier** than both EXIF and Date Created → use **Date Modified**.
  3. If no EXIF data → fallback to the **earliest** between `Date Modified` and `Date Created`.

- **Clean standardized naming format:** 
	IMG_ddmmyy_hhmmAM/PM.ext
	*Example:* IMG_250929_1103AM.jpg


- **Automatic duplicate handling:**  
	When multiple files have the same timestamp, a suffix `_1`, `_2`, etc., is added:
	IMG_250929_1103AM.jpg
	IMG_250929_1103AM_1.jpg

- **Supported image formats:** jpg, jpeg, png, gif, webp, bmp, tif, tiff
- **Dry-run mode:** Preview results before renaming any files.
- **Recursive directory processing:** Rename files in all subdirectories with `--recursive`.
- **Rollback support:** Automatically generates a CSV mapping file for easy restoration to original filenames.

---
## 📦 Installation
### Requirements:
- Python **3.8+**
- Required Python packages:
- `Pillow`
- `piexif`
### Install for all users (global installation on Windows)
```bash
pip install pillow piexif
```
### Or for the current user only:
```bash
pip install --user pillow piexif
```

---
## 💻 Usage

Run the script with the following command structure:
```bash
python rename_images_by_date.py <command> [options]
```

Available commands:
- `rename` → Rename images
- `rollback` → Restore images to their original names using the CSV mapping file
### 1. Rename images in a folder
```bash
python rename_images_by_date.py rename --dir "./photos"
```
### 2. Rename images recursively (including subfolders)
```bash
python rename_images_by_date.py rename --dir "./photos" --recursive
```
### 3. Preview results without renaming (dry-run)
> **Recommended:** Always run in dry-run mode first to ensure the output looks correct.
```bash
python rename_images_by_date.py rename --dir "./photos" --recursive --dry-run
```
### 4. Rollback from CSV mapping
> If you need to restore original filenames:
```bash
python rename_images_by_date.py rollback --map "./photos/rename_logs.csv"
```

---
## 🗂 Example
### Initial folder structure:
```yaml
photos/
├── DSC_0001.jpg    (EXIF = 2025:09:29 11:03:12)
├── vacation.png    (No EXIF, Modified = 2023-07-01 22:05:00)
└── IMG_2020.tiff   (EXIF = 2025:09:29 11:03:12)
```
### Dry-run command:
```bash
python rename_images_by_date.py rename --dir "./photos" --recursive --dry-
```
### Output:
```yaml
[DRY-RUN] photos/DSC_0001.jpg -> photos/IMG_290925_1103AM.jpg
[DRY-RUN] photos/vacation.png -> photos/IMG_010723_1005PM.png
[DRY-RUN] photos/IMG_2020.tiff -> photos/IMG_290925_1103AM_1.tiff

=== SUMMARY ===
Total images found: 3
Renamed (simulated): 3
Conflicts resolved: 1
Errors: 0
Mapping file saved at: photos/rename_logs.csv
[NOTE] This was a dry-run. No files were actually renamed.
```

---
## 🗂 Project Structure

```yaml
RID/
│
├── main.py                        # Main script
├── README.md                      # Documentation
└── samples/                       # Example folder (optional)
```

---
## 📝 Safe Workflow Recommendations

1. **Step 1:** Run the command with `--dry-run` to preview changes.
2. **Step 2:** Review the generated CSV mapping file for accuracy.
3. **Step 3:** Run the rename command without `--dry-run` to apply changes.
4. **Step 4:** Use `rollback` with the same CSV file if you need to restore the original filenames.
    

---
## ⚠️ Notes

- Ensure you have **write permissions** for the target directory.
- Files currently open in another program may trigger a `PermissionError`.
- Always keep a backup of your images before bulk renaming.
- The rollback process depends on the **exact CSV mapping file** generated during the rename operation.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to submit a pull request or open an issue if you:
- Find a bug 🐛
- Have a feature request ✨
- Want to improve the documentation 📚

---

## 📜 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute this software with proper attribution.

---