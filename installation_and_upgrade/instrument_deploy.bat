set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
rem set "RELEASE-SUFFIX="
call "%~dp0\define_latest_genie_python.bat"

git --version

IF ERRORLEVEL 1 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    EXIT /b %errorlevel%
)

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

IF EXIST "C:\Instrument\Apps\EPICS" (
  call C:\Instrument\Apps\EPICS\config_env.bat
  set PYTHONDIR=%LATEST_PYTHON_DIR%
  set PYTHONHOME=%LATEST_PYTHON_DIR%
  set PYTHONPATH=%LATEST_PYTHON_DIR%
  call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_pre_stop
  IF ERRORLEVEL 1 EXIT /b %errorlevel%
  start /wait cmd /c "%STOP_IBEX%")
)

REM Set python as share just for script call
SETLOCAL
set PYTHONDIR=%LATEST_PYTHON_DIR%
set PYTHONHOME=%LATEST_PYTHON_DIR%
set PYTHONPATH=%LATEST_PYTHON_DIR%

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_main
IF ERRORLEVEL 1 EXIT /b %errorlevel%
ENDLOCAL

start /wait cmd /c "%START_IBEX%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_post_start
IF ERRORLEVEL 1 EXIT /b %errorlevel%
