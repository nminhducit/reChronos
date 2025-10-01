# reChronos - Bring order to your chaotic filesystem

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

An interactive CLI tool to recursively rename files based on their creation/modification dates with full rollback support.

## ✨ Features

- 🔄 **Recursive Renaming** - Processes all files in subfolders
- 📅 **Smart Date Detection** - Uses oldest date (created or modified) closest to when photo was taken
- 🌍 **Unicode Support** - Works with Vietnamese and special characters in paths
- ↩️ **Full Rollback** - Undo rename operations with single command
- 📝 **Operation Logging** - Tracks all operations in CSV format
- 🎨 **Colored Output** - Beautiful terminal interface with colorama
- 🔒 **Safe Operations** - Confirmation prompts and collision handling

## 📋 Rename Format

Files are renamed to: `EXT_YYMMDD_HHMMAMPM.ext`

**Examples:**
- `photo.jpg` → `JPG_241001_0230PM.jpg`
- `document.pdf` → `PDF_240915_1045AM.pdf`
- `video.mp4` → `MP4_240820_0815PM.mp4`
- `noext` → `FILE_241001_0100AM`

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 💻 Usage

### Run the Program

```bash
python rechronos.py
```

### Available Commands

| Command           | Description         | Example               |
|-------------------|---------------------|-----------------------|
| `preview [path]`  | Preview rename plan | `preview C:\Photos`   |
| `rename [path]`   | Execute rename      | `rename C:\Downloads` |
| `rollback [path]` | Undo last batch     | `rollback C:\Photos`  |
| `help`            | Show help           | `help`                |
| `quit` / `exit`   | Exit program        | `quit`                |

### Examples

#### Preview files before renaming
```
reChronos@root# preview "C:\Users\ADMIN\Downloads"
1. photo1.jpg → JPG_241001_0230PM.jpg
2. document.pdf → PDF_240915_1045AM.pdf
Total files planned: 2
```

#### Rename files
```
reChronos@root# "C:\Users\ADMIN\Pictures"
Proceed with rename? (yes/no): yes
  photo1.jpg → JPG_241001_0230PM.jpg
  photo2.jpg → JPG_241001_0231PM.jpg
Batch 20241001153555 completed: 2 files renamed
```

#### Rollback changes
```
reChronos@root# rollback "C:\Users\ADMIN\Pictures"
Rollback last batch? (yes/no): yes
✓ Rolled back: JPG_241001_0230PM.jpg → photo1.jpg
✓ Rolled back: JPG_241001_0231PM.jpg → photo2.jpg
Rollback complete: 2/2 files restored
```

## 📁 Project Structure

```yaml
reChronos/
├─ src/
│  └─ rechronos.py                # main source (entrypoint)
├─ assets/
│  └─ rechronos_icon.png          # editable source PNG for icon
│  └─ rechronos.ico               # generated .ico (optional to commit)
├─ build_scripts/
│  └─ make_icon.py                # script to generate .ico from PNG
│  └─ build_exe.ps1               # PowerShell build helper (Windows)
│  └─ build_exe.sh                # Bash helper (Linux/macOS)
├─ ci/
│  └─ windows-build.yml           # Optional: GitHub Actions workflow (example)
├─ tests/
│  └─ sample_files/               # small sample files for demo (sanitized)
│  └─ test_readme_usage.md
├─ docs/
│  └─ usage.md                    # extended docs (optional)
├─ .github/
│  └─ workflows/
│     └─ release.yml              # optional GH Actions to build & release exe
├─ .gitignore
├─ README.md
├─ LICENSE
├─ requirements.txt
└─ CONTRIBUTING.md (optional)
```

## 🔨 Building Executable

### On Windows with PowerShell:

Install PyInstaller:
```bash
pyinstaller --onefile --icon assets/rechronos.ico --uac-admin src/rechronos.py
```

### On Linux/macOS:
```bash
pyinstaller --onefile src/rechronos.py
```

Output will be in `dist/rechronos.exe`

## 📊 Log File Format

Operations are logged in `rename_log.csv` inside each processed directory:

| Column    | Description                            |
|-----------|----------------------------------------|
| batch_id  | Unique batch identifier (timestamp)    |
| timestamp | ISO format timestamp                   |
| src       | Source file path (absolute)            |
| dst       | Destination file path (absolute)       |
| action    | Operation type (rename/rollback/error) |

## ⚠️ Important Notes

1. **Backup Important Files** - Always backup before mass renaming
2. **Test First** - Use `preview` to verify before `rename`
3. **Log Files** - Keep `rename_log.csv` for rollback capability
4. **Path Support** - Supports spaces and Unicode characters in paths
5. **Collision Handling** - Automatically resolves name conflicts

## 🐛 Troubleshooting

### "No log found to rollback"
- Ensure `rename_log.csv` exists in the target directory
- Rollback only works on directories previously renamed by reChronos

### "Invalid directory" error
- Check path spelling and use quotes for paths with spaces
- Use forward slashes `/` or double backslashes `\\` in paths

### Files not renaming
- Check file permissions
- Ensure files are not open in other programs
- Run as administrator if needed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

NMINHDUCIT

- GitHub: [@nminhducit](https://github.com/nminhducit)

## 🙏 Acknowledgments

- Built with [Colorama](https://github.com/tartley/colorama) for cross-platform colored output
- Inspired by the need for better photo organization

## 📮 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Contact: nminhducit@gmail.com

---

⭐ **If you find this project useful, please give it a star!** ⭐