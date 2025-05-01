setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
REM call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

REM start /wait cmd /c "%STOP_IBEX%"

call c:\instrument\apps\python3\python.exe "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step developer_update
IF ERRORLEVEL 1 (
  set errcode = %ERRORLEVEL%
  call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
  EXIT /b !errcode!
)

REM start /wait cmd /c "%START_IBEX%"
REM call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
