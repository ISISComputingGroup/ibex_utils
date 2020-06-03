setlocal
REM Remove old builds from the archive
call "%~dp0..\installation_and_upgrade\define_latest_genie_python.bat"
set PYTHONUNBUFFERED=TRUE
call "%LATEST_PYTHON%" "%~dp0purge_archive.py"

set "AGESTORE=c:\Program Files (x86)\Windows Kits\10\Debuggers\x64\agestore.exe"
set "KITROOT=\\isis\inst$\Kits$\CompGroup\ICP"
if exist "%AGESTORE%" (
    "%AGESTORE%" %KITROOT%\EPICS\Symbols -days=90 -q -y -s
    "%AGESTORE%" %KITROOT%\ISISICP\Symbols -days=90 -q -y -s
)
