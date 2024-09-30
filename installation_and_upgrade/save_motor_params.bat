setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0define_latest_genie_python.bat"
IF %errorlevel% neq 0 goto ERROR

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step save_motor_params

IF %errorlevel% neq 0 goto ERROR

call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
exit /b 0

:ERROR
    set errcode = %ERRORLEVEL%
    call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
    EXIT /b !errcode!
