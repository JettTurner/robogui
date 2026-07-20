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

for /f "tokens=2 delims==" %%v in ('findstr /r "__version__" src\version.py') do set VER=%%~v
echo Updating installer version to %VER%
powershell -Command "(Get-Content 'robocopy_Installer.iss') -replace 'AppVersion=.*', 'AppVersion=%VER%' | Set-Content 'robocopy_Installer.iss'"

pause
