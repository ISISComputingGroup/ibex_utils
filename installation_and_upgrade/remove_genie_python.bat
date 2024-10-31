@echo off

if "%~1"=="" (
    @echo No path provided as the first parameter.
    goto ERROR
)

set "remove_genie_python_path=%~1"

REM Checks that supplied filepath exists.
if exist "%remove_genie_python_path%" (

    REM Checks that "Python_Build_" is in the supplied filepath, so it is a python build.
    echo.%remove_genie_python_path% | findstr /C:"Python_Build_">nul && (

        REM Deletes directory tree + quiet.
        RMDIR /S /Q %remove_genie_python_path%

        REM Unassigns environment variables.
        set LATEST_PYTHON_DIR=
        set LATEST_PYTHON=
        set LATEST_PYTHON3=

        @echo Successfully removed "%remove_genie_python_path%" and unset genie build variables. 
        set remove_genie_python_path=
        exit /b 0

    ) || (
        @echo "%remove_genie_python_path%" is not a python build directory.
        goto ERROR
    )

) else (
    @echo Could not find the specified path: "%remove_genie_python_path%".
    goto ERROR
)

:ERROR
set remove_genie_python_path=
@echo remove_genie_python failed
exit /b 1
