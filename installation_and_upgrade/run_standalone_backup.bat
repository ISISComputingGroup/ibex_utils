@ECHO OFF
setlocal
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%
call cd "%~dp0"
set PYTHONPATH=.
@REM Uses Python from the Shares, set as LATEST_PYTHON
call "%LATEST_PYTHON%" "%~dp0ibex_install_utils\tasks\backup_tasks.py"
call rmdir /s /q %UV_TEMP_VENV%
endlocal
