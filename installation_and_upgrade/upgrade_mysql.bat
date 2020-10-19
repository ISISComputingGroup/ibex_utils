set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat" 3

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

start /wait cmd /c "%STOP_IBEX%"
set "LATEST_PYTHON=C:\Instrument\Apps\Python3\python.exe"
call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step force_upgrade_mysql
IF ERRORLEVEL 1 EXIT /b %errorlevel%

start /wait cmd /c "%START_IBEX%"
