setlocal
call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%
set PYTHONUNBUFFERED=TRUE
REM use LATEST_PYTHON3 so not killed by stop_ibex_server 
call "%LATEST_PYTHON3%" -u "%~dp0check_builds_are_recent.py"
call "%~dp0..\installation_and_upgrade\remove_genie_python.bat" %LATEST_PYTHON_DIR%
