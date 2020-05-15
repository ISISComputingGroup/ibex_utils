set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

REM Use a locally installed python in C:\users\<username>\Documents\Python as we don't want to execute code directly from
REM a network share as the admin user.
call "C:\Users\Administrator\Documents\Python\python.exe" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" mount_vhds --quiet
IF ERRORLEVEL 1 EXIT /b %errorlevel%

call "C:\Users\Administrator\Documents\Python\python.exe" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" dismount_vhds --quiet
IF ERRORLEVEL 1 EXIT /b %errorlevel%
