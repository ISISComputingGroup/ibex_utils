@ECHO OFF
setlocal
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"
set PYTHONPATH=.
@REM Might want to use Python in Instruments/
%LATEST_PYTHON% ibex_install_utils\tasks\backup_tasks.py
endlocal
