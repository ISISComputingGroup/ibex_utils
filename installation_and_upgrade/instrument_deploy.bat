setlocal EnableDelayedExpansion

REM Prompt user if running console with Administrative privileges.
net session >nul 2>&1
if !errorLevel! equ 0 (
    echo You are in Administrative mode. This may cause file permissioning problems during IBEX setup.
    CHOICE /C YN /M "Are you sure you want to continue: "
    IF !errorLevel! equ 1 goto permissiongranted
    exit /b 1
)
:permissiongranted

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
rem set "RELEASE-SUFFIX="

git --version

if %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    goto ERROR
)

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

IF EXIST "C:\Instrument\Apps\EPICS" (
  REM use python 3 for pre stop as requires genie
  SETLOCAL
  call "%~dp0define_latest_genie_python.bat"
  call C:\Instrument\Apps\EPICS\config_env.bat
  set "PYTHONDIR=!LATEST_PYTHON_DIR!"
  set "PYTHONHOME=!LATEST_PYTHON_DIR!"
  set "PYTHONPATH=!LATEST_PYTHON_DIR!"
  call "!LATEST_PYTHON!" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_pre_stop
  IF !errorlevel! neq 0 goto ERROR
  start /wait cmd /c "%STOP_IBEX%"
  ENDLOCAL
)

REM Set python as share just for script call
call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 goto ERROR

SETLOCAL
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_main
IF %errorlevel% neq 0 goto ERROR
ENDLOCAL

start /wait cmd /c "%START_IBEX%"

REM python should be installed correctly at this point, so use local python
set "LATEST_PYTHON_DIR=C:\Instrument\Apps\Python3\"
set "LATEST_PYTHON=%LATEST_PYTHON_DIR%python.exe"
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_post_start
:ERROR
EXIT /b %errorlevel%
