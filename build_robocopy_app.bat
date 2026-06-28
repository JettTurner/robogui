@echo off
rmdir /s /q build
rmdir /s /q dist

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "ROBOGUI" ^
  --icon "icon\robogui.ico" ^
  --add-data "icon;icon" ^
  src\robogui.py

pause
