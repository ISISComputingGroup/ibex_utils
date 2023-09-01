setlocal EnableDelayedExpansion
REM Prompt user if running console with Administrative privileges.
net session >nul 2>&1
if !errorLevel! equ 0 (
    echo You are in Administrative mode. This may cause later file permissioning problems during IBEX setup.
    CHOICE /C YN /M "Are you sure you want to continue: "
    IF !errorLevel! neq 1 exit /b 1
)
if "%USERNAME%" == "gamekeeper" (
    echo You are using the gamekeeper account. This may cause later file permissioning problems during IBEX setup.
    CHOICE /C YN /M "Are you sure you want to continue: "
    IF !errorLevel! neq 1 exit /b 1
)

exit /b 0
