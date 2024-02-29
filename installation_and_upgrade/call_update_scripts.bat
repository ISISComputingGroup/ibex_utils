setlocal

call
installation_and_upgrade\pythonwrap.bat .\installation_and_upgrade installation_and_upgrade\ibex_install_utils\tasks\update_scripts.py
if %errorlevel% neq 0 exit /b %errorlevel%
