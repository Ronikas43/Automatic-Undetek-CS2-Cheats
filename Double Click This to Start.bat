@echo off
setlocal EnableDelayedExpansion

set REQUIRED_MAJOR=3
set REQUIRED_MINOR=10

echo Checking Python...

:: Check if Python actually runs
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found or not working.
    echo.
    echo Please install Python manually:
    echo 1. Your browser will open https://www.python.org/downloads/windows/
    echo 2. Go to "Latest stable release"
    echo 3. Use Admin privileges when installing py.exe
    echo 4. Make sure to check "Add Python to PATH"
    echo.
    echo Press any key to open the download page...
    pause >nul
    start https://www.python.org/downloads/windows/
    echo After installing Python, run this script again.
    pause
    exit /b
)

:: Get Python version
for /f "tokens=2 delims= " %%A in ('python --version 2^>^&1') do set PY_VERSION=%%A
for /f "tokens=1,2 delims=." %%A in ("%PY_VERSION%") do (
    set PY_MAJOR=%%A
    set PY_MINOR=%%B
)

echo Detected Python version %PY_VERSION%

:: Check version requirement
if !PY_MAJOR! LSS %REQUIRED_MAJOR% goto python_outdated
if !PY_MAJOR! EQU %REQUIRED_MAJOR% if !PY_MINOR! LSS %REQUIRED_MINOR% goto python_outdated

echo Python version OK.
goto install_packages

:python_outdated
echo Your Python version (%PY_VERSION%) is older than %REQUIRED_MAJOR%.%REQUIRED_MINOR%.
echo Please install the latest stable Python version from:
echo https://www.python.org/downloads/windows/
echo Make sure to use Admin privileges for py.exe and check "Add Python to PATH".
pause
start https://www.python.org/downloads/windows/
exit /b

:install_packages
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

call :check_install undetected-chromedriver
call :check_install selenium
call :check_install setuptools
call :check_install pyautogui

goto run_script

:check_install
python -m pip show %1 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing %1 ...
    python -m pip install %1
) else (
    echo %1 already installed.
)
exit /b

:run_script
echo Running Automatic.py...
python "%~dp0Automatic.py"

pause