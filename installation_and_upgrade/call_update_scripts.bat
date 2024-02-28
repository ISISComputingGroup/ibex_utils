setlocal
call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%
set "PYTHONPATH=."
"%LATEST_PYTHON%" %~dp0ibex_install_utils\tasks\update_scripts.py
REM c:\instrument\apps\python3\python.exe %~dp0ibex_install_utils\tasks\update_scripts.py
if %errorlevel% neq 0 exit /b %errorlevel%
