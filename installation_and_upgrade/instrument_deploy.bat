REM instrument_deploy.bat - used for upgrading IBEX on an instrument PC.

setlocal EnableDelayedExpansion

REM check if console has Administrative privileges
call "%~dp0check_for_admin_console.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
set SERVER_ARCH=x64
if not "%1" == "" set SERVER_ARCH=%1

if not exist "%SOURCE%" (
    @echo Cannot access network share %SOURCE%
    @echo If this computer is an instrument, check whether D: drive in explorer is showing
    @echo as disconnected. If it is, click on it in explorer to reconnect then try this
    @echo script again. If there are no D: or O: network drives mapped in explorer, then
    @echo you will need to to provide network credentials for access - see wiki
    @echo https://github.com/ISISComputingGroup/ibex_developers_manual/wiki/Deployment-on-an-Instrument-Control-PC 
    goto ERROR
)

git --version

if %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    exit /b %errorlevel%
)

call "%~dp0set_epics_ca_addr_list.bat"
call "%~dp0install_or_update_uv.bat"
call "%~dp0set_up_venv.bat"
if %errorlevel% neq 0 goto ERROR

set "STOP_IBEX=C:\Instrument\Apps\EPICS\stop_ibex_server"
set "START_IBEX=C:\Instrument\Apps\EPICS\start_ibex_server"

IF EXIST "C:\Instrument\Apps\EPICS" (

  call python "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_deploy_pre_stop
  IF !errorlevel! neq 0 exit /b !errorlevel!
  start /wait cmd /c "%STOP_IBEX%"
  ENDLOCAL
)

REM Copy the pydev command history file to temp so it can be copied back in after deploy (otherwise it is overwritten)
REM this is also done in client install bat, but as we remove client pre-install we need to do it here
REM too or else it is lost using this route
set "GENIECMDLOGFILE=history.py"
set "GENIECMDLOGDIR=C:\Instrument\Apps\Client_E4\workspace\.metadata\.plugins\org.python.pydev.shared_interactive_console"
if exist "%GENIECMDLOGDIR%\%GENIECMDLOGFILE%" (
	@echo Copying pydev history file before deleting client
	robocopy "%GENIECMDLOGDIR%" "%TEMP%" "%GENIECMDLOGFILE%" /R:2 /IS /NFL /NDL /NP /NC /NS /LOG:NUL
)

REM Create the "GALIL_OLD.txt" or "GALIL_NEX.txt" file in tmp dir
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

REM stop_ibex_server calls config_env which means we have to reactivate our venv
call %UV_TEMP_VENV%\scripts\activate

call python "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_deploy_main
IF %errorlevel% neq 0 exit /b %errorlevel%
ENDLOCAL

start /i /wait cmd /c "%START_IBEX%"

REM start_ibex_server calls config_env which means we have to reactivate our venv
call python "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --server_arch %SERVER_ARCH% --confirm_step instrument_deploy_post_start
call rmdir /s /q %UV_TEMP_VENV%

exit /b 0

:ERROR
call rmdir /s /q %UV_TEMP_VENV%
EXIT /b 1
