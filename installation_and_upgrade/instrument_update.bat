set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases\4.0.0"

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

C:\Instrument\Apps\Python\python.exe IBEX_upgrade.py --release_dir "%SOURCE%" --confirm_step instrument_update
IF ERRORLEVEL 1 GOTO :EOF

start /wait cmd /c "%START_IBEX%"
