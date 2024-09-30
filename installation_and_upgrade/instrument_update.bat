setlocal
call "%~dp0define_latest_genie_python.bat"
if %errorlevel% neq 0 goto ERROR
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases\4.0.0"

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_update
if %errorlevel% neq 0 goto ERROR
start /wait cmd /c "%START_IBEX%"

call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
exit /b 0

:ERROR
set errcode = %ERRORLEVEL%
call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
EXIT /b !errcode!
