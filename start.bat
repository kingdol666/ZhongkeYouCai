@echo off
setlocal
title Film Thickness Heatmap Analysis - Launcher

echo ============================================
echo Start Film Thickness Heatmap Analysis System
echo ============================================
echo.

:: ============================================================
:: Find or install Python 3.11
:: ============================================================
set "PYTHON_EXE="

:: Try system python first
where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; sys.exit(0 if sys.version_info[:2]==(3,11) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=python"
        echo [OK] System Python is 3.11
        goto :install_deps
    ) else (
        for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [SKIP] System Python is %%v, need 3.11
    )
)

:: Check common installation paths
for %%d in (
    "C:\Python311"
    "C:\Program Files\Python311"
    "C:\Program Files (x86)\Python311"
) do (
    if exist "%%~d\python.exe" (
        set "PYTHON_EXE=%%~d\python.exe"
        echo [OK] Found Python 3.11 at %%~d
        goto :install_deps
    )
)

:: Check LOCALAPPDATA / APPDATA
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    echo [OK] Found Python 3.11 in LocalAppData
    goto :install_deps
)
if exist "%APPDATA%\Python\Python311\python.exe" (
    set "PYTHON_EXE=%APPDATA%\Python\Python311\python.exe"
    echo [OK] Found Python 3.11 in AppData
    goto :install_deps
)

:: ============================================================
:: Download embeddable Python 3.11
:: ============================================================
echo [WARN] Python 3.11 not found, downloading...
set "PYTHON_DIR=%~dp0python311"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

if exist "%PYTHON_EXE%" (
    echo [OK] Local Python 3.11 already exists
    goto :install_deps
)

set "PYTHON_ZIP=%TEMP%\python-3.11.9-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"

echo [DOWNLOAD] Fetching Python 3.11.9 ...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UseBasicParsing" >nul 2>&1
if errorlevel 1 (
    curl -L -o "%PYTHON_ZIP%" "%PYTHON_URL%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to download Python
        echo         Please install Python 3.11 manually:
        echo         https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo [EXTRACT] Extracting to %PYTHON_DIR% ...
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Extraction failed
    pause
    exit /b 1
)

:: Enable pip in embedded Python
set "PTH_FILE=%PYTHON_DIR%\python311._pth"
if exist "%PTH_FILE%" (
    powershell -Command "(Get-Content '%PTH_FILE%') -replace '#import site', 'import site' | Set-Content '%PTH_FILE%'" >nul 2>&1
)

:: Install pip
echo [SETUP] Installing pip ...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%TEMP%\get-pip.py' -UseBasicParsing" >nul 2>&1
"%PYTHON_EXE%" "%TEMP%\get-pip.py" --no-warn-script-location >nul 2>&1

del "%PYTHON_ZIP%" >nul 2>&1
del "%TEMP%\get-pip.py" >nul 2>&1
echo [OK] Python 3.11 ready

:: ============================================================
:: Install dependencies
:: ============================================================
:install_deps
echo.
echo [INSTALL] Installing dependencies ...
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt" -q --disable-pip-version-check
if errorlevel 1 (
    echo [WARN] Some dependencies failed to install
)

:: ============================================================
:: Launch
:: ============================================================
echo.
echo [LAUNCH] Starting application ...
echo ============================================
echo.

cd /d "%~dp0"

:: Start simulation tool in a new window
start "Production Simulator" "%PYTHON_EXE%" "tools\simulate_production.py"

:: Start main application
"%PYTHON_EXE%" "run_ui.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with code: %errorlevel%
    pause
)
exit /b 0
