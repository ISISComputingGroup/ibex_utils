setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

call "%~dp0set_epics_ca_addr_list.bat"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
if %errorlevel% neq 0 goto ERROR

@echo.
@echo *** This will not do a deploy but you will be asked to confirm upgrade type
@echo *** IBEX should still be running at this point
@echo.
call python "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_deploy_pre_stop
if %errorlevel% neq 0 goto ERROR

call rmdir /s /q %UV_TEMP_VENV%
exit /b 0

:ERROR
set errcode = %ERRORLEVEL%
call rmdir /s /q %UV_TEMP_VENV%
EXIT /b !errcode!
