REM Install latest version of IBEX

REM argument 1 is CLEAN or INCR for type of build touse (default: CLEAN)

REM argument 2 is a server build prefix
REM normally will use EPICS_win7_x64 or EPICS_CLEAN_win7_x64 depending on incremental/clean
REM with prefix specified will use {prefix}_win7_x64 and {prefix}_CLEAN_win7_x64 for server install source directory
setlocal EnableDelayedExpansion

set PYTHONUNBUFFERED=TRUE

call "%~dp0\define_latest_genie_python.bat"
IF %errorlevel% neq 0 GOTO ERROR

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server.bat"
IF EXIST "C:\Instrument\Apps\EPICS" (
    call "%STOP_IBEX%"
) else (
    REM in case one has been left around running in the background
    taskkill /f /im caRepeater.exe
)

if not "%2" == "" (
    @echo Using server build prefix %2
    set SERVER_BUILD_PREFIX=--server_build_prefix "%2"
)
set INSTALL_TYPE=install_latest
if "%1" == "INCR" (
    set INSTALL_TYPE=install_latest_incr
)
set "RELEASE_SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

if "%1" == "RELEASE" (
    REM set INSTALL_TYPE=instrument_install
    REM set INSTALL_TYPE=training_update
    set INSTALL_TYPE=install_latest
    call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%RELEASE_SOURCE%" --quiet !INSTALL_TYPE!
) else (
    call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --kits_icp_dir "%KITS_ICP_PATH%"  %SERVER_BUILD_PREFIX% --quiet !INSTALL_TYPE!
)
IF %errorlevel% neq 0 GOTO ERROR

GOTO :EOF

:ERROR
echo "Error on Install"
exit /b 2
