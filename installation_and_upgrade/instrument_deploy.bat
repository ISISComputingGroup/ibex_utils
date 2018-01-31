set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases\4.2.0"
call "%~dp0\define_latest_genie_python.bat"

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

IF EXIST "C:\Instrument\Apps\EPICS" (
  call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_deploy_pre_stop
  IF ERRORLEVEL 1 EXIT /b %errorlevel%
  start /wait cmd /c "%STOP_IBEX%")
)

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_deploy_main
IF ERRORLEVEL 1 EXIT /b %errorlevel%

start /wait cmd /c "%START_IBEX%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_deploy_post_start
IF ERRORLEVEL 1 EXIT /b %errorlevel%
