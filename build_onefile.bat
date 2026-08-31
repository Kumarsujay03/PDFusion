@echo off
REM PDFusion - Single EXE Build Script
REM Creates a single portable executable (larger file, slower startup)

echo ============================================
echo  PDFusion - Single EXE Build
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH.
    pause
    exit /b 1
)

REM Install deps
echo [1/3] Checking dependencies...
pip install -r requirements.txt >nul 2>&1
pip install pyinstaller >nul 2>&1

echo.
echo [2/3] Building single executable...
echo This will take several minutes...
echo.

python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "PDFusion" ^
    --add-data "app/config/settings.json;app/config" ^
    --add-data "app/resources;app/resources" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "fitz" ^
    --hidden-import "pikepdf" ^
    --hidden-import "PIL" ^
    --hidden-import "docx" ^
    --hidden-import "reportlab" ^
    --exclude-module "tkinter" ^
    --exclude-module "matplotlib" ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo ============================================
echo  Output: dist\PDFusion.exe
echo ============================================
echo.

pause
