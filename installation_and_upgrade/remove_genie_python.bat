@echo off

if "%~1"=="" (
    @echo No path provided as the first parameter.
    goto ERROR
)

set substring=Python_Build_
set path=%~1
set modified_path=%path:%substring%=%

if "%path%" neq "%modified_path%" (

    RMDIR /S /Q %path% && @echo Successfully removed %path%.

    set LATEST_PYTHON_DIR=
    set LATEST_PYTHON=
    set LATEST_PYTHON3=


) else (
    @echo Could not find the specified path: %path%.
    goto ERROR
)

exit /b 0

:ERROR
@echo remove_genie_python failed
exit /b 1
