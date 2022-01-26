setlocal EnableDelayedExpansion
REM Prompt user if running console with Administrative privileges.
net session >nul 2>&1
if !errorLevel! equ 0 (
    echo You are in Administrative mode. This may cause file permissioning problems during IBEX setup.
    CHOICE /C YN /M "Are you sure you want to continue: "
    IF !errorLevel! equ 1 goto permissiongranted
    exit /b 1
)
:permissiongranted
exit /b 0
