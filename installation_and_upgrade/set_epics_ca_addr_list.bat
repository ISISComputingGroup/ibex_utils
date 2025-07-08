rem @echo off

set MYIP=127.0.0.1
for /f "usebackq tokens=2 delims=:" %%f in (`ipconfig ^| findstr /c:"IPv4 Address" ^| findstr 130.246.`) do (
    set MYIP=%%f
    goto :done
)
:done
set MYGATE=127.0.0.1
for /f "usebackq tokens=2 delims=:" %%f in (`ipconfig ^| findstr /c:"Default Gateway" ^| findstr 130.246.`) do (
    set MYGATE=%%f
    goto :done2
)
:done2
set ISISIP=%MYIP: =%
set ISISGATE=%MYGATE: =%

if "%ISISGATE%" == "130.246.48.254" set ISISBCAST=130.246.51.255
if "%ISISGATE%" == "130.246.52.254" set ISISBCAST=130.246.55.255
if "%ISISGATE%" == "130.246.36.254" set ISISBCAST=130.246.39.255
if "%ISISGATE%" == "130.246.56.254" set ISISBCAST=130.246.59.255

set "EPICS_CA_ADDR_LIST=127.255.255.255 %ISISBCAST% 130.246.39.152:5066 %EPICS_CA_ADDR_LIST%"
set "EPICS_CA_AUTO_ADDR_LIST=NO"
set "EPICS_CA_MAX_ARRAY_BYTES=20000000"
