setlocal
call "%~dp0..\installation_and_upgrade\install_or_update_uv.bat"
call "%~dp0..\installation_and_upgrade\set_up_venv.bat"

set PYTHONUNBUFFERED=TRUE

call python -u "%~dp0check_builds_are_recent.py"
