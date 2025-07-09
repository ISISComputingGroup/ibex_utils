setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

call "%~dp0set_epics_ca_addr_list.bat"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
IF %errorlevel% neq 0 goto ERROR

git --version

IF %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    goto ERROR
)

call python "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step update_icp
IF %errorlevel% neq 0 goto ERROR
call rmdir /s /q %UV_TEMP_VENV%
exit /b 0

:ERROR
set errcode = %ERRORLEVEL%
call rmdir /s /q %UV_TEMP_VENV%
EXIT /b !errcode!
