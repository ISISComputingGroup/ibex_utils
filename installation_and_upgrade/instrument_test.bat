setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
if %errorlevel% neq 0 goto ERROR

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_test
if %errorlevel% neq 0 goto ERROR

call rmdir /s /q %UV_TEMP_VENV%

exit /b 0

:ERROR
call rmdir /s /q %UV_TEMP_VENV%
EXIT /b 1
