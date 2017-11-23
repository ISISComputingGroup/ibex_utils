REM Install latest version of IBEX

call "%~dp0\define_latest_genie_python.bat"

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --kits_icp_dir "%KITS_ICP_PATH%"  --quiet install_latest
IF ERRORLEVEL 1 GOTO :ERROR

start /wait cmd /c "%START_IBEX%"
popd
GOTO :EOF

:ERROR
popd
exit /b 2
