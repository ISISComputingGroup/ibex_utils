set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
rem set "RELEASE-SUFFIX="
call "%~dp0\define_latest_genie_python.bat"

git --version

IF ERRORLEVEL 1 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    goto ERROR
)

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

IF EXIST "C:\Instrument\Apps\EPICS" (
  call C:\Instrument\Apps\EPICS\config_env.bat
  SETLOCAL
  set PYTHONDIR=%LATEST_PYTHON_DIR%
  set PYTHONHOME=%LATEST_PYTHON_DIR%
  set PYTHONPATH=%LATEST_PYTHON_DIR%
  call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" instrument_deploy_pre_stop_7_0_0
  IF ERRORLEVEL 1 goto ERROR
  ENDLOCAL
  start /wait cmd /c "%STOP_IBEX%")
)

REM Set python as share just for script call
SETLOCAL
set PYTHONDIR=%LATEST_PYTHON_DIR%
set PYTHONHOME=%LATEST_PYTHON_DIR%
set PYTHONPATH=%LATEST_PYTHON_DIR%

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" instrument_deploy_main_7_0_0
IF ERRORLEVEL 1 goto ERROR
ENDLOCAL

start /wait cmd /c "%START_IBEX%"

REM python should be installed correctly at this point, so use local python
call "C:\Instrument\Apps\Python\python.exe" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" instrument_deploy_post_start_7_0_0
:ERROR
EXIT /b %errorlevel%

REM we want most machines back off again after we install IBEX for testing. Otherwise they will fill up log files etc
start /wait cmd /c "%STOP_IBEX%"
