REM Upgrade a training machine

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"
IF EXIST "C:\Instrument\Apps\EPICS" (start /wait cmd /c "%STOP_IBEX%")

call "%SOURCE%\genie_python\Python\python.exe" IBEX_upgrade.py --release_dir "%SOURCE%" --quiet training_update
IF %ERRORLEVEL% neq 0 (
    @echo install failed
	exit /b %ERRORLEVEL%
)

start /wait cmd /c "%START_IBEX%"
