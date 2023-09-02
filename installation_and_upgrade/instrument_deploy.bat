setlocal EnableDelayedExpansion

REM check if console has Administrative privileges
call "%~dp0check_for_admin_console.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
set SERVER_ARCH=x64
if not "%1" == "" set SERVER_ARCH=%1

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
  call "!LATEST_PYTHON!" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_deploy_pre_stop
  IF !errorlevel! neq 0 goto ERROR
  start /wait cmd /c "%STOP_IBEX%"
  ENDLOCAL
)

REM Copy the pydev command history file to temp so it can be copied back in after deploy (otherwise it is overwritten)
REM this is also done in client install bat, but as we remove client pre-install we need to do it here
REM too or else it is lost using this route
set "GENIECMDLOGFILE=history.py"
set "GENIECMDLOGDIR=C:\Instrument\Apps\Client_E4\workspace\.metadata\.plugins\org.python.pydev.shared_interactive_console"
if exist "%GENIECMDLOGDIR%\%GENIECMDLOGFILE%" (
	@echo Copying pydev history file before deleting client
	robocopy "%GENIECMDLOGDIR%" "%TEMP%" "%GENIECMDLOGFILE%" /R:2 /IS /NFL /NDL /NP /NC /NS /LOG:NUL
)

REM Set python as share just for script call
call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 goto ERROR

SETLOCAL
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_deploy_main 
IF %errorlevel% neq 0 goto ERROR
ENDLOCAL

start /wait cmd /c "%START_IBEX%"

REM python should be installed correctly at this point, so use local python
set "LATEST_PYTHON_DIR=C:\Instrument\Apps\Python3\"
set "LATEST_PYTHON=%LATEST_PYTHON_DIR%python.exe"
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_deploy_post_start
:ERROR
EXIT /b %errorlevel%
