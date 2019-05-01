@echo off
REM Get latest python build and kits icp path
REM   KITS_ICP_PATH is set to ICP directory
REM   LATEST_PYTHON is set to a version on genie_python that can be run

pushd \\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP

set KITS_ICP_PATH=%cd%

if exist "%KITS_ICP_PATH%\genie_python\LATEST_BUILD.txt" (
	for /f %%i in ( %KITS_ICP_PATH%\genie_python\LATEST_BUILD.txt ) do (
	    set LATEST_PYTHON_DIR=%KITS_ICP_PATH%\genie_python\BUILD-%%i\Python\
	    set LATEST_PYTHON=%KITS_ICP_PATH%\genie_python\BUILD-%%i\Python\python.exe
	)
) else (
	@echo Could not access LATEST_BUILD.txt
	goto ERROR
)

@echo LATEST PYTHON: %LATEST_PYTHON%

goto :EOF

:ERROR
popd
@echo update_genie_python failed
exit /b 1
