setlocal
set "PYTHONHOME=%1"
set "PYTHONPATH=%PYTHONHOME%"
@echo Updating %PYTHONHOME% to latest versions of genie_python and ibex_bluesky_core
"%PYTHONHOME%\python.exe" -m pip install genie_python[plot]@git+https://github.com/IsisComputingGroup/genie.git@main
if %errorlevel% NEQ 0 EXIT /B %errorlevel%
"%PYTHONHOME%\python.exe" -m pip install ibex_bluesky_core@git+https://github.com/IsisComputingGroup/ibex_bluesky_core.git@main
if %errorlevel% NEQ 0 EXIT /B %errorlevel%
