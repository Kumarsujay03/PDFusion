@echo off
REM PDFusion - Build Script for Windows
REM Creates a standalone executable using PyInstaller

echo ============================================
echo  PDFusion - Build Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.13+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if pip packages are installed
echo [1/4] Checking dependencies...
pip show PySide6 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

echo.
echo [2/4] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo [3/4] Building executable...
echo This may take several minutes...
echo.

python -m PyInstaller pdfusion.spec --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo ============================================
echo  Output: dist\PDFusion\
echo  Executable: dist\PDFusion\PDFusion.exe
echo ============================================
echo.
echo You can distribute the entire "dist\PDFusion" folder.
echo.

pause
