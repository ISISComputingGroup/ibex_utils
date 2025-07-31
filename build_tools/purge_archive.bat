setlocal EnableDelayedExpansion
REM Remove old builds from the archive

set "WORKWIN=%WORKSPACE:/=\%"

if "%WORKWIN%" == "" (
    call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat"
) else (
    if exist "%WORKWIN%\Python3" rd /s /q %WORKWIN%\Python3
    if !errorlevel! neq 0 exit /b 1
    call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat" %WORKWIN%\Python3
)
IF %errorlevel% neq 0 EXIT /b %errorlevel%

set PYTHONUNBUFFERED=TRUE
REM use LATEST_PYTHON3 to avoid process being killed
"%LATEST_PYTHON3%" -u "%~dp0purge_archive.py"
set errcode=!errorlevel!
@echo purge_archive.py exited with code !errcode!

@echo Deleting build branches directories
set "KITROOT=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP"
pushd %KITROOT%
if !errorlevel! equ 0 (
    set MYDIR=!CD!
    for /d %%i in ( !MYDIR!\Client_E4 !MYDIR!\genie_python_3 !MYDIR!\script_generator !MYDIR!\Client_E4_win11 ) do (
        if exist "%%i\branches" (
            @echo Deleting in %%i\branches
            forfiles /p "%%i\branches" /d -60 /s /m BUILD-* /c "cmd /c rd /q /s \\?\@path >NUL"
        )
    )
)
popd

for /F "skip=1" %%I in ('wmic path win32_localtime get dayofweek') do (set /a DOW=%%I 2>NUL)
if %DOW% neq 6 (
    @echo Skipping debug symbol cleanup as day of week %DOW% is not 6
    CALL "%~dp0..\installation_and_upgrade\remove_genie_python.bat" %LATEST_PYTHON_DIR%
    exit /b !errcode!
)

REM Remove old debug symbols from the archive
set "AGESTORE=c:\Program Files (x86)\Windows Kits\10\Debuggers\x64\agestore.exe"
set "KITROOT=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP"
if exist "%AGESTORE%" (
    pushd "%KITROOT%\EPICS\Symbols"
    "%AGESTORE%" . -days=90 -q -y -s
    set errcode=!errorlevel!
    popd
    @echo agestore exited with code !errcode!
    REM we do not yet know when an isisicp version stops being used, we need to tie it to a release better
    REM "%AGESTORE%" %KITROOT%\ISISICP\Symbols -days=90 -q -y -s
) else (
    @echo agestore does not exist
)

CALL "%~dp0..\installation_and_upgrade\remove_genie_python.bat" %LATEST_PYTHON_DIR%
