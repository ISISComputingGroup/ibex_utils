setlocal EnableDelayedExpansion

REM check if console has Administrative privileges
call "%~dp0check_for_admin_console.bat"
if %errorlevel% neq 0 goto ERROR

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0define_latest_genie_python.bat"
if %errorlevel% neq 0 goto ERROR

set SERVER_ARCH=x64
if not "%1" == "" set SERVER_ARCH=%1

if not exist "%SOURCE%" (
    @echo Cannot access network share %SOURCE%
    @echo If this computer is an instrument, check whether D: drive in explorer is showing
    @echo as disconnected. If it is, click on it in explorer to reconnect then try this
    @echo script again. If there are no D: or O: network drives mapped in explorer, then
    @echo you will need to to provide network credentials for access - see wiki
    @echo https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Deployment-on-an-Instrument-Control-PC 
    exit /b 1
)

git --version
IF %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    goto ERROR
)

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

REM Set python as share just for script call
SETLOCAL
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_install
if %errorlevel% neq 0 goto ERROR
ENDLOCAL

start /wait cmd /c "%START_IBEX%"

call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
exit /b 0

:ERROR
set errcode = %ERRORLEVEL%
call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
EXIT /b !errcode!
