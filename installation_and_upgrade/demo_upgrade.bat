REM Upgrade NDXDEMO for sprint review

set "SERVER_SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\EPICS\EPICS_win7_x64\BUILD-3125\EPICS"
set "CLIENT_SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Client\BUILD179"
set "GENIE_PYTHON=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\genie_python\BUILD-146"

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

call "%GENIE_PYTHON%\Python\python.exe" IBEX_upgrade.py --server_dir "%SERVER_SOURCE%" --client_dir "%CLIENT_SOURCE%" --quiet demo_upgrade
IF ERRORLEVEL 1 GOTO :EOF

start /wait cmd /c "%START_IBEX%"
