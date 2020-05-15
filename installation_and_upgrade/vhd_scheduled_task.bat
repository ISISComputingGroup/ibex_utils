REM fake a release directory as admin can't access network shares. It's not actually needed but the script falls over without it.
set "SOURCE=C:\Users\Administrator\Documents\fake_release_dir"

REM Use a locally installed python in C:\users\<username>\Documents\Python as we don't want to execute code directly from
REM a network share as the admin user.
call "C:\Users\Administrator\Documents\Python\python.exe" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" mount_vhds --quiet
IF %ERRORLEVEL% neq 0 EXIT /b %errorlevel%

call "C:\Users\Administrator\Documents\Python\python.exe" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" dismount_vhds --quiet
IF %ERRORLEVEL% neq 0 EXIT /b %errorlevel%
