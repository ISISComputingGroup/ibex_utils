@ECHO OFF
setlocal
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0set_epics_ca_addr_list.bat"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%
call python "%~dp0ibex_install_utils\tasks\backup_tasks.py"
call rmdir /s /q %UV_TEMP_VENV%
endlocal
