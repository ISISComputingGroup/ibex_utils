REM Upgrade a training machine

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

REM Set python as share just for script call
call "%~dp0\define_latest_genie_python.bat" 3
SETLOCAL
set PYTHONDIR=%LATEST_PYTHON_DIR%
set PYTHONHOME=%LATEST_PYTHON_DIR%
set PYTHONPATH=%LATEST_PYTHON_DIR%

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --quiet training_update
IF ERRORLEVEL 1 goto ERROR
ENDLOCAL

start /wait cmd /c "%START_IBEX%"

:ERROR
EXIT /b %errorlevel%