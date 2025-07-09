setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"

IF %errorlevel% neq 0 EXIT /b %errorlevel%

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

start /wait cmd /c "%STOP_IBEX%"

call "%LATEST_PYTHON%" -u "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step force_upgrade_mysql

IF %errorlevel% neq 0 (
    set errcode = %ERRORLEVEL%
    call rmdir /s /q %UV_TEMP_VENV%
    EXIT /b !errcode!
)

start /wait cmd /c "%START_IBEX%"
call rmdir /s /q %UV_TEMP_VENV%
