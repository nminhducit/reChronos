# Build Windows exe with admin rights + icon
pyinstaller --onefile --icon ../assets/rechronos.ico --uac-admin ../src/rechronos.py
