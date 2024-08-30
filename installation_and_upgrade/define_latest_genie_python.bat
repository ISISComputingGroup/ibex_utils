@echo off
setlocal enabledelayedexpansion
REM Get latest python build and kits icp path
REM KITS_ICP_PATH is set to ICP directory
REM LATEST_PYTHON is set to a version on genie_python that can be run

REM	Fetch newest python build from \\isis\inst$\Kits$\CompGroup\ICP\genie_python_3
REM Use genie_python_install to install it into a temporary directory
REM Need to make sure that after every use of this bat that these variables are undefined and the temp dir is removed

set "KITS_ICP_PATH=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP"
set "genie_dir=%KITS_ICP_PATH%\genie_python_3"

if exist "%genie_dir%\LATEST_BUILD.txt" (

	for /f %%i in ( %genie_dir%\LATEST_BUILD.txt ) do (

		if "%~1" NEQ "" (
			set "LATEST_PYTHON_DIR=%~1\Python_Build_%%i" 
		) else (
			set "LATEST_PYTHON_DIR=%tmp%\Python_Build_%%i"
		)
		
		mkdir !LATEST_PYTHON_DIR!
	
		%genie_dir%\BUILD-%%i\genie_python_install.bat !LATEST_PYTHON_DIR!
		
	    set LATEST_PYTHON=!LATEST_PYTHON_DIR!\python.exe
	    set LATEST_PYTHON3=!LATEST_PYTHON_DIR!\python3.exe
		
	)
	
) else (

	@echo Could not access LATEST_BUILD.txt
	goto ERROR
	
)

rem @echo LATEST PYTHON: %LATEST_PYTHON%

exit /b 0

:ERROR
@echo define_latest_genie_python failed
exit /b 1
