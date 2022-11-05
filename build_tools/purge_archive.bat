setlocal
REM Remove old builds from the archive
call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat" 3
set PYTHONUNBUFFERED=TRUE
"%LATEST_PYTHON%" -u "%~dp0purge_archive.py"

REM Remove old debug symbols from the archive
set "AGESTORE=c:\Program Files (x86)\Windows Kits\10\Debuggers\x64\agestore.exe"
set "KITROOT=\\isis\inst$\Kits$\CompGroup\ICP"
if exist "%AGESTORE%" (
    "%AGESTORE%" %KITROOT%\EPICS\Symbols -days=90 -q -y -s
    REM we do not yet know when an isisicp version stops being used, we need to tie it to a release better
    REM "%AGESTORE%" %KITROOT%\ISISICP\Symbols -days=90 -q -y -s
)
