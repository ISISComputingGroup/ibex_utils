@echo off
setlocal

REM arg 1 is DAE type (2 or 3), default is DAE2

if "%1" == "" (
    set "DAETYPE=2"
) else (
    set "DAETYPE=%1"
)

set "BASEDIR=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\ISISICP\DAE%DAETYPE%"

if exist "%BASEDIR%\LATEST_BUILD.txt" (
	for /f %%i in ( %BASEDIR%\LATEST_BUILD.txt ) do (
	    set "SOURCE=%BASEDIR%\%%i"
	)
) else (
	@echo Could not access LATEST_BUILD.txt
	goto ERROR
)

call "%SOURCE%\update_inst.cmd"

if %errorlevel% neq 0 (
    @echo Error installing ISISICP
    exit /b %errorlevel%
)

goto :EOF

:ERROR
@echo install_latest_isisicp failed
exit /b 1
