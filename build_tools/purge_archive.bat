REM Remove old builds from the archive
call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat"
set PYTHONUNBUFFERED=TRUE
call "%LATEST_PYTHON%" "%~dp0purge_archive.py"
REM define_latest_genie_python does a pushd
