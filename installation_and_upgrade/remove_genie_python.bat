@echo off

if "%~1"=="" (
    echo No path provided as the first parameter.
    exit /b 1
)

set substring=Python_Build_
set path=%~1
set modified_path=%path:%substring%=%

if "%path%" neq "%modified_path%" (
    
    set LATEST_PYTHON_DIR=
    set LATEST_PYTHON=
    set LATEST_PYTHON3=

    RMDIR /S /Q %path%

) else (
    echo Could not find the specified path: %path%.
)