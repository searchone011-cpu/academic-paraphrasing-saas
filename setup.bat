@echo off
echo ============================================================
echo   DIGITAL ALCHEMIST X-1 - Academic AI-Humanization Tool
echo ============================================================
echo.

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    echo [OK] Python found: py
) else (
    python --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON=python
        echo [OK] Python found: python
    ) else (
        echo [ERROR] Python not found. Please install Python 3.8+
        pause
        exit /b 1
    )
)

if not exist "venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON% -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

echo [INFO] Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
echo [OK] pip ready.

echo [INFO] Installing packages...
venv\Scripts\pip.exe install deep-translator langdetect --quiet
echo [OK] Packages installed.

echo.
echo ============================================================
echo   Launching application...
echo ============================================================
echo.

venv\Scripts\python.exe app\main.py 2>&1
echo.
echo ============================================================
echo   EXIT CODE: %errorlevel%
echo ============================================================
echo.
if %errorlevel% neq 0 (
    echo [ERROR] Application closed with an error. See above for details.
)
echo Press any key to close...
pause > nul