REM Install latest version of IBEX

REM argument 1 is CLEAN or INCR for type of build touse (default: CLEAN)

REM argument 2 is a server build prefix
REM normally will use EPICS_win7_x64 or EPICS_CLEAN_win7_x64 depending on incremental/clean
REM with prefix specified will use {prefix}_win7_x64 and {prefix}_CLEAN_win7_x64 for server install source directory
setlocal

set PYTHONUNBUFFERED=TRUE

call "%~dp0\define_latest_genie_python.bat" 3

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server.bat"
IF EXIST "C:\Instrument\Apps\EPICS" (call "%STOP_IBEX%")

if not "%2" == "" (
    @echo Using server build prefix %2
    set SERVER_BUILD_PREFIX=--server_build_prefix "%2"
)
set INSTALL_TYPE=install_latest
if "%1" == "INCR" (
    set INSTALL_TYPE=install_latest_incr
)

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --kits_icp_dir "%KITS_ICP_PATH%"  %SERVER_BUILD_PREFIX% --quiet %INSTALL_TYPE%
set errcode=%ERRORLEVEL%
popd
IF %errcode% neq 0 GOTO :ERROR

GOTO :EOF

:ERROR
echo "Error on Install"
exit /b 2
