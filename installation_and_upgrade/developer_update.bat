set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

start /wait cmd /c "%STOP_IBEX%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step developer_update
IF ERRORLEVEL 1 EXIT /b %errorlevel%

start /wait cmd /c "%START_IBEX%"
