setlocal EnableDelayedExpansion
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0define_latest_genie_python.bat"
if %errorlevel% neq 0 goto ERROR
call C:\Instrument\Apps\EPICS\config_env.bat
set "PYTHONDIR=%LATEST_PYTHON_DIR%"
set "PYTHONHOME=%LATEST_PYTHON_DIR%"
set "PYTHONPATH=%LATEST_PYTHON_DIR%"
@echo.
@echo *** This will not do a deploy but you will be asked to confirm upgrade type
@echo *** IBEX should still be running at this point
@echo.
call "%LATEST_PYTHON%" -u "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step instrument_deploy_pre_stop
if %errorlevel% neq 0 goto ERROR

call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
exit /b 0

:ERROR
set errcode = %ERRORLEVEL%
call "%~dp0remove_genie_python.bat" %LATEST_PYTHON_DIR%
EXIT /b !errcode!
