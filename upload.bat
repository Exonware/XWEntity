@echo off
REM Unified Upload Command for eXonware Projects - Windows Batch Wrapper
REM Company: eXonware.com
REM Author: Eng. Muhammad AlShehri
REM Email: connect@exonware.com
REM Version: 0.0.1
REM Generation Date: January 27, 2025

echo.
echo ================================================================================
echo eXonware Unified Project Uploader
echo Company: eXonware.com
echo Author: Eng. Muhammad AlShehri
echo ================================================================================
echo.

REM Check if required parameters are provided
if "%~1"=="" (
    echo ERROR: Project version is required
    echo.
    echo Usage:
    echo   upload_project.bat ^<project_version^> ^<python_version^> [project_path]
    echo.
    echo Examples:
    echo   upload_project.bat 0.0.1.3 3.8
    echo   upload_project.bat 0.0.2.0 3.9
    echo   upload_project.bat 0.0.1.5 3.8 C:\path\to\project
    echo.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: Python version is required
    echo.
    echo Usage:
    echo   upload_project.bat ^<project_version^> ^<python_version^> [project_path]
    echo.
    echo Examples:
    echo   upload_project.bat 0.0.1.3 3.8
    echo   upload_project.bat 0.0.2.0 3.9
    echo   upload_project.bat 0.0.1.5 3.8 C:\path\to\project
    echo.
    pause
    exit /b 1
)

set PROJECT_VERSION=%~1
set PYTHON_VERSION=%~2
set PROJECT_PATH=%~3

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Look for upload_project.py in tools/ci/ directory relative to current project
set PYTHON_SCRIPT=%SCRIPT_DIR%..\tools\ci\upload_project.py

REM Check if upload_project.py exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: upload_project.py not found at %PYTHON_SCRIPT%
    echo Please ensure the script is in the tools/ci/ directory
    pause
    exit /b 1
)

REM If no project path specified, use current directory
if "%PROJECT_PATH%"=="" (
    set PROJECT_PATH=.
)

echo Starting unified upload process...
echo Project Version: %PROJECT_VERSION%
echo Python Version: %PYTHON_VERSION%
if not "%PROJECT_PATH%"=="" (
    echo Project Path: %PROJECT_PATH%
) else (
    echo Project Path: Current directory
)
echo.

REM Run the Python upload script
if "%PROJECT_PATH%"=="" (
    python "%PYTHON_SCRIPT%" %PROJECT_VERSION% %PYTHON_VERSION%
) else (
    python "%PYTHON_SCRIPT%" %PROJECT_VERSION% %PYTHON_VERSION% %PROJECT_PATH%
)

REM Check if the script ran successfully
if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! Project uploaded successfully!
    echo Project Version: %PROJECT_VERSION%
    echo Python Version: %PYTHON_VERSION%
    echo ================================================================================
    echo.
    echo What was done:
    echo   ✅ Configuration files updated
    echo   ✅ Version references updated
    echo   ✅ Centralized version.py created/updated
    echo   ✅ Project published to GitHub
    echo   ✅ Project published to PyPI
    echo.
    echo You can now:
    echo   1. Check your GitHub repository for the new release
    echo   2. Install the updated package: pip install [package_name]
    echo   3. Verify the package on PyPI
    echo.
    goto :success
)

echo.
echo ================================================================================
echo ERROR! Project upload failed!
echo Project Version: %PROJECT_VERSION%
echo Python Version: %PYTHON_VERSION%
echo ================================================================================
echo.
echo Please check the error messages above and try again.
echo Common issues:
echo   - Make sure you're in the correct project directory
echo   - Check that pyproject.toml exists
echo   - Verify Git is configured properly
echo   - Ensure PyPI credentials are set up
echo.

:success
echo Upload process completed!

:end
echo Press any key to exit...
pause >nul
