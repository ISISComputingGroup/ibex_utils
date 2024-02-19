set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step save_motor_params
IF %errorlevel% neq 0 EXIT /b %errorlevel%
