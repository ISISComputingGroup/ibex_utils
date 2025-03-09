setlocal EnableDelayedExpansion
set PYTHONUNBUFFERED=1
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

IF EXIST "C:\Instrument\Apps\EPICS\stop_ibex_server.bat" (
  start /wait cmd /c "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
)

call "%LATEST_PYTHON%" -u "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" create_vhds --quiet --no_log_to_var

IF %ERRORLEVEL% NEQ 0 (
  set errcode = %ERRORLEVEL%
  call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
  EXIT /b !errcode!
)

call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
