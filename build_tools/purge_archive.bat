REM Remove old builds from the archive
call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat"
call "%LATEST_PYTHON%" "%~dp0purge_archive.py"
