@echo off
echo ============================================================
echo   DIGITAL ALCHEMIST X-1 - Auto Fix Script
echo ============================================================
echo.
echo [INFO] Removing conflicting old files...

cd /d "%~dp0"

if exist "app\gui.py" (
    del /f /q "app\gui.py"
    echo [OK] Deleted app\gui.py
) else (
    echo [SKIP] app\gui.py not found
)

if exist "app\core\engine.py" (
    del /f /q "app\core\engine.py"
    echo [OK] Deleted app\core\engine.py
) else (
    echo [SKIP] app\core\engine.py not found
)

if exist "app\core\docx_processor.py" (
    del /f /q "app\core\docx_processor.py"
    echo [OK] Deleted app\core\docx_processor.py
) else (
    echo [SKIP] app\core\docx_processor.py not found
)

if exist "app\core\humanizer.py" (
    del /f /q "app\core\humanizer.py"
    echo [OK] Deleted app\core\humanizer.py
) else (
    echo [SKIP] app\core\humanizer.py not found
)

echo.
echo [INFO] Checking required files...

set MISSING=0

if not exist "app\main.py" (
    echo [ERROR] MISSING: app\main.py
    set MISSING=1
) else (
    echo [OK] app\main.py exists
)

if not exist "app\core\text_processor.py" (
    echo [ERROR] MISSING: app\core\text_processor.py
    set MISSING=1
) else (
    echo [OK] app\core\text_processor.py exists
)

if not exist "app\gui\main_window.py" (
    echo [ERROR] MISSING: app\gui\main_window.py
    set MISSING=1
) else (
    echo [OK] app\gui\main_window.py exists
)

if %MISSING%==1 (
    echo.
    echo [ERROR] Some required files are missing!
    echo Please re-download the files from the instructions.
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] All checks passed. Launching application...
echo ============================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    py -m venv venv
    echo [OK] Virtual environment created.
    echo [INFO] Installing packages...
    venv\Scripts\pip.exe install deep-translator langdetect --quiet
    echo [OK] Packages installed.
)

venv\Scripts\python.exe app\main.py 2>&1
echo.
echo ============================================================
echo   EXIT CODE: %errorlevel%
echo ============================================================
if %errorlevel% neq 0 (
    echo [ERROR] Application error. See details above.
)
echo.
echo Press any key to close...
pause > nul
