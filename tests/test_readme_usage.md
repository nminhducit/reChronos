# Test reChronos Usage

## Input files
img1.jpg
doc1.txt
script.sh


## Run
```bash
python src/rechronos.py rename --dir ./tests/sample_files --recursive
```

## Expected preview
img1.jpg → JPG_250930_1021AM.jpg
doc1.txt → TXT_250930_1021AM.txt
script.sh → SH_250930_1021AM.sh

## After confirm
Files renamed. Rollback supported.

# reChronos Usage Guide
This document provides **detailed instructions** and **examples** beyond the README.

## CLI Syntax
rechronos.py [command] [options]

### Commands
- `rename` – bulk rename files
- `rollback` – rollback last operation

### Options
- `--dir <path>` – directory to scan
- `--recursive` – scan recursively
- `--max-show <N>` – limit preview lines

---

## Rollback
After rename, a mapping file is saved:
/rename_log.csv

You can rollback by:
```bash
python src/rechronos.py rollback \\tests\sample_file\
```

---

## Advanced
- Customize prompt style in source.
- Integrate with CI for auto-build releases.
