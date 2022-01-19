setlocal
REM this is ran by an MDT configured system to complete tasks after VHDs are mounted
REM we will already have an installed IBEX system

set PYTHONUNBUFFERED=1
set "KITS_ICP_PATH=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP"
set "SOURCE=%KITS_ICP_PATH%\Releases"

IF EXIST "C:\Instrument\Apps\EPICS\stop_ibex_server.bat" (
  start /wait cmd /c "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
)

call "C:\Instrument\Apps\Python3\python.exe" -u "%~dp0IBEX_upgrade.py" --client_dir="%TEMP%" --server_dir="%TEMP%" --client_e4_dir="%TEMP%" --genie_python3_dir="%TEMP%" run_vhd_post_install --quiet
IF %ERRORLEVEL% NEQ 0 EXIT /b %errorlevel%
