set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
rem set "RELEASE-SUFFIX="
call "%~dp0\define_latest_genie_python.bat"

git --version

REM IF ERRORLEVEL 1 (
REM     echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
REM     EXIT /b %errorlevel%
REM )

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

IF EXIST "C:\Instrument\Apps\EPICS" (
  call C:\Instrument\Apps\EPICS\config_env.bat
  call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_pre_stop
  IF ERRORLEVEL 1 EXIT /b %errorlevel%
  start /wait cmd /c "%STOP_IBEX%")
)

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_main
IF ERRORLEVEL 1 EXIT /b %errorlevel%

start /wait cmd /c "%START_IBEX%"

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step instrument_deploy_post_start
IF ERRORLEVEL 1 EXIT /b %errorlevel%
