@echo off
setlocal
cd /d "%~dp0"
echo === 1/3  Python environment ===
if not exist .venv ( python -m venv .venv || goto :err )
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt || goto :err

echo === 2/3  Building FXHotkeys.exe ===
pyinstaller --noconfirm --clean --windowed --name FXHotkeys --icon assets\icon.ico --add-data "assets;assets" main.py || goto :err

echo === 3/3  Building the installer ===
set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe
if exist "%ISCC%" (
  "%ISCC%" installer.iss || goto :err
  echo.
  echo DONE:  installer_output\FXHotkeys-Setup.exe
) else (
  echo Inno Setup 6 not found - install it from https://jrsoftware.org/isdl.php and run build.bat again.
  echo The portable app is ready in dist\FXHotkeys\FXHotkeys.exe
)
pause
exit /b 0
:err
echo BUILD FAILED
pause
exit /b 1
