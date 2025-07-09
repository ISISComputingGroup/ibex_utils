REM Install latest version of IBEX
REM argument 1 is CLEAN, INCR or RELEASE for type of build touse (default: CLEAN)
REM argument 2 is a server build prefix
REM  normally will use EPICS_win7_x64 or EPICS_CLEAN_win7_x64 depending on incremental/clean
REM  with prefix specified will use {prefix}_win7_x64 and {prefix}_CLEAN_win7_x64 for server install source directory
REM argument 3 can be x86 or x64, defaults to x64 if not specified.
REM  this will change e.g. {prefix}_win7_x64  to {prefix}_win7_x86   as server source directory to use
REM argument 4 can be server winbuild, defaults to win7 if not specified.
REM  this will change e.g. {prefix}_win7_x64  to {prefix}_win1_x64   as server source directory to use

setlocal EnableDelayedExpansion

set PYTHONUNBUFFERED=TRUE

call "%~dp0set_epics_ca_addr_list.bat"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
if %errorlevel% neq 0 goto ERROR

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server.bat"
IF EXIST "C:\Instrument\Apps\EPICS" (
    call "%STOP_IBEX%"
    REM stop_ibex_server calls config_env which means we have to reactivate our venv
    call "%~dp0_activate_venv.bat"
) else (
    REM in case one has been left around running in the background
    taskkill /f /im caRepeater.exe
)

if not "%2" == "" (
    @echo Using server build prefix %2
    set SERVER_BUILD_PREFIX=--server_build_prefix "%2"
)

set SERVER_ARCH=x64
if not "%3" == "" set SERVER_ARCH=%3
@echo Using server arch %SERVER_ARCH%

set SERVER_WINBUILD=win7
if not "%4" == "" set SERVER_WINBUILD=%4
@echo Using server winbuild %SERVER_WINBUILD%

set INSTALL_TYPE=install_latest
if "%1" == "INCR" (
    set INSTALL_TYPE=install_latest_incr
)
set "RELEASE_SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"

REM Copy the pydev command history file to temp so it can be copied back in after deploy (otherwise it is overwritten)
REM this is also done in client install bat, but as we remove client pre-install we need to do it here
REM too or else it is lost using this route
set "GENIECMDLOGFILE=history.py"
set "GENIECMDLOGDIR=C:\Instrument\Apps\Client_E4\workspace\.metadata\.plugins\org.python.pydev.shared_interactive_console"
if exist "%GENIECMDLOGDIR%\%GENIECMDLOGFILE%" (
	@echo Copying pydev history file before deleting client
	robocopy "%GENIECMDLOGDIR%" "%TEMP%" "%GENIECMDLOGFILE%" /R:2 /IS /NFL /NDL /NP /NC /NS /LOG:NUL
)

REM Create the "GALIL_OLD.txt" or "GALIL_NEW.txt" file in tmp dir
REM to inform the IBEX Server installation step which Galil version to use
set "GALIL_OLD_FILE=GALIL_OLD.txt"
set "GALIL_NEW_FILE=GALIL_NEW.txt"
set "GALIL_DIR=C:\Instrument\Apps\EPICS\ioc\master\GALIL"
set "GALIL_OLD_DIR=C:\Instrument\Apps\EPICS\ioc\master\GALIL-OLD"
if exist "%TEMP%\%GALIL_OLD_FILE%" del "%TEMP%\%GALIL_OLD_FILE%"
if exist "%TEMP%\%GALIL_NEW_FILE%" del "%TEMP%\%GALIL_NEW_FILE%"
if exist "%GALIL_DIR%\%GALIL_OLD_FILE%" (
    @echo Detected old Galil driver - %GALIL_OLD_FILE% in %GALIL_DIR%
    robocopy "%GALIL_DIR%" "%TEMP%" "%GALIL_OLD_FILE%" /R:2 /IS /NFL /NDL /NP /NC /NS /LOG:NUL
    set "DETECT_OLD_GALIL=YES"
)
if exist "%GALIL_OLD_DIR%\%GALIL_OLD_FILE%" (
    REM GALIL-OLD has not been renamed to GALIL hence we must be using new driver
    @echo Detected new Galil driver - %GALIL_OLD_FILE% in %GALIL_OLD_DIR%
    copy /y "%GALIL_OLD_DIR%\%GALIL_OLD_FILE%" "%TEMP%\%GALIL_NEW_FILE%"
    set "DETECT_NEW_GALIL=YES"
)
if "%DETECT_OLD_GALIL%" == "YES" (
    if "%DETECT_NEW_GALIL%" == "YES" (
        @echo ERROR - both NEW and OLD GALIL driver appear enabled, this should not be possible
        exit /b 1
    )
)

if "%1" == "RELEASE" (
    REM set INSTALL_TYPE=instrument_install
    REM set INSTALL_TYPE=training_update
    set INSTALL_TYPE=install_latest
    python "%~dp0IBEX_upgrade.py" --release_dir "%RELEASE_SOURCE%" --server_arch %SERVER_ARCH% --quiet !INSTALL_TYPE! --server_winbuild %SERVER_WINBUILD%
) else (
    python "%~dp0IBEX_upgrade.py" --kits_icp_dir "%KITS_ICP_PATH%"  %SERVER_BUILD_PREFIX% --server_arch %SERVER_ARCH% --quiet !INSTALL_TYPE! --server_winbuild %SERVER_WINBUILD%
)
IF %errorlevel% neq 0 (
    echo Error %errorlevel% returned from IBEX_upgrade script
    GOTO ERROR
)

if not "%1" == "RELEASE" (
    call "%~dp0update_genie_python_module.bat" C:\Instrument\Apps\Python3
)
IF %errorlevel% neq 0 (
    echo Error %errorlevel% returned from update_genie_python_module.bat
    GOTO ERROR
)

call rmdir /s /q %UV_TEMP_VENV%
GOTO :EOF

:ERROR
echo Error on Install
call rmdir /s /q %UV_TEMP_VENV%
exit /b 2
