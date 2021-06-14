@echo off
REM Get latest python build and kits icp path
REM   KITS_ICP_PATH is set to ICP directory
REM   LATEST_PYTHON is set to a version on genie_python that can be run

set "KITS_ICP_PATH=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP"

set "GENIE_DIR=%KITS_ICP_PATH%\genie_python_3"

if exist "%GENIE_DIR%\LATEST_BUILD.txt" (
	for /f %%i in ( %GENIE_DIR%\LATEST_BUILD.txt ) do (
	    set LATEST_PYTHON_DIR=%GENIE_DIR%\BUILD-%%i\Python\
	    set LATEST_PYTHON=%GENIE_DIR%\BUILD-%%i\Python\python.exe
	)
) else (
	@echo Could not access LATEST_BUILD.txt
	goto ERROR
)

@echo LATEST PYTHON: %LATEST_PYTHON%

exit /b 0

:ERROR
@echo define_latest_genie_python failed
exit /b 1
