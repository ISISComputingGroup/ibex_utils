@ECHO OFF
setlocal
set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"
call cd "%~dp0"
set PYTHONPATH=.
@REM Uses Python from the Shares, set as LATEST_PYTHON
call "%LATEST_PYTHON%" "%~dp0ibex_install_utils\tasks\backup_tasks.py"
endlocal
