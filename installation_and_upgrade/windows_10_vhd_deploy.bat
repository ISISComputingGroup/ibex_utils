set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
set "SUFFIX=%1"

REM likewise we can assume that python 3 exists as we just installed a VHD
call C:\instrument\apps\python3\python.exe "%~dp0windows_10_vhd_deploy.py"
IF %errorlevel% neq 0 EXIT /b %errorlevel%
ENDLOCAL

start /wait cmd /c "%START_IBEX%"
