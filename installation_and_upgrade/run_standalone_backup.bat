@ECHO OFF
setlocal
set PYTHONPATH=.
@REM Might want to use Python in Instruments/
python ibex_install_utils\tasks\backup_tasks.py
endlocal