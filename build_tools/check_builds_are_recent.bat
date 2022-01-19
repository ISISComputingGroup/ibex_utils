call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat" 3
set PYTHONUNBUFFERED=TRUE
call "%LATEST_PYTHON%" "%~dp0check_builds_are_recent.py"
