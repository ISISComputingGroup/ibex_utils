set PYTHONUNBUFFERED=1
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"

IF EXIST "C:\Instrument\Apps\EPICS\stop_ibex_server.bat" (
  start /wait cmd /c "C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
)

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --kits_icp_dir "%KITS_ICP_PATH%" create_vhds --quiet
IF %ERRORLEVEL% NEQ 0 EXIT /b %errorlevel%
