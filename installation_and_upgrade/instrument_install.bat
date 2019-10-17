setlocal

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
set "SUFFIX=%1"
call "%~dp0\define_latest_genie_python.bat"
IF %errorlevel% neq 0 (
    echo Cannot define latest python.
    EXIT /b %errorlevel%
)

git --version
IF %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    EXIT /b %errorlevel%
)

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

REM Set python as share just for script call
SETLOCAL
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_install
IF %errorlevel% neq 0 EXIT /b %errorlevel%
ENDLOCAL

start /wait cmd /c "%START_IBEX%"
