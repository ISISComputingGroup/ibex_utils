setlocal EnableDelayedExpansion
REM Remove old builds from the archive
call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat" 3

if not "%WORKSPACE%" == "" (
    if exist "%WORKSPACE%\Python3" rd /s /q %WORKSPACE%\Python3
    call %LATEST_PYTHON_DIR%..\genie_python_install.bat %WORKSPACE%\Python3
    if !errorlevel! neq 0 exit /b 1
    set "LATEST_PYTHON3=%WORKSPACE%\Python3\python3.exe"
)

set PYTHONUNBUFFERED=TRUE
REM use LATEST_PYTHON3 to avoid process being killed 
"%LATEST_PYTHON3%" -u "%~dp0purge_archive.py"
set errcode=!errorlevel!
@echo purge_archive.py exited with code !errcode!
for /F "skip=1" %%I in ('wmic path win32_localtime get dayofweek') do (set /a DOW=%%I 2>NUL)
if %DOW% neq 6 (
    @echo Skipping debug symbol cleanup as day of week %DOW% is not 6
    exit /b !errcode"
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
