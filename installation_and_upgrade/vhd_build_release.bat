setlocal EnableDelayedExpansion
set PYTHONUNBUFFERED=1
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

call "%~dp0set_epics_ca_addr_list.bat"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

IF EXIST "C:\Instrument\Apps\EPICS\stop_ibex_server.bat" (
  start /wait cmd /c "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
)

call "%~dp0_activate_venv.bat"
call python -u "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" create_vhds --quiet --no_log_to_var

IF %ERRORLEVEL% NEQ 0 (
  set errcode = %ERRORLEVEL%
  call rmdir /s /q %UV_TEMP_VENV%
  EXIT /b !errcode!
)

call rmdir /s /q %UV_TEMP_VENV%
