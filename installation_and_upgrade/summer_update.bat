setlocal EnableDelayedExpansion

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

git --version

IF %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    EXIT /b %errorlevel%
)

xcopy /y  %SOURCE%\15.0.0\EPICS\utils\logrotate.py c:\instrument\apps\epics\utils
IF %errorlevel% neq 0 goto ERROR

for %%t in ( truncate_database upgrade_mysql update_calibrations_repository setup_log_rotation ) do (
    call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step %%t
    IF !errorlevel! neq 0 goto ERROR
)

echo Finished
pause
exit /b 0

:ERROR
echo ERROR - see messages above and install log
pause
exit /b 1
