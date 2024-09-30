setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 goto ERROR

git --version

IF %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    goto ERROR
)

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step truncate_database
IF %errorlevel% neq 0 goto ERROR
call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%

exit /b 0

:ERROR
set errcode = %ERRORLEVEL%
call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
EXIT /b !errcode!