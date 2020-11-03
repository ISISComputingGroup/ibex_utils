set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
set "SUFFIX=%1"

REM since we just installed a VHD, can assume that config_env exists
call c:\instrument\apps\epics\config_env.bat

REM likewise we can assume that python 3 exists as we just installed a VHD
call C:\instrument\apps\python3\python.exe "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step windows_10_vhd_deploy
IF %errorlevel% neq 0 EXIT /b %errorlevel%
ENDLOCAL

start /wait cmd /c "%START_IBEX%"
