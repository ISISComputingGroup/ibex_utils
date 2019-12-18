@echo off
setlocal EnableDelayedExpansion

set /A errors = 0

set support_error=""

if exist C:\Instrument\Apps\EPICS\support\%1 (
    pushd C:\Instrument\Apps\EPICS\support\%1\master
    make clean uninstall && make
    popd
) else (
    if exist C:\Instrument\Apps\EPICS\ISIS\%1 (
        pushd C:\Instrument\Apps\EPICS\ISIS\%1\master
        make clean uninstall && make
        popd
    ) else (
        set support_error=CANNOT FIND SUPPORT OR ISIS MODULE
        set /A errors += 1
        echo !support_error!
    )
)

set ioc_error=""

if exist C:\Instrument\Apps\EPICS\ioc\master\%2 (
    pushd C:\Instrument\Apps\EPICS\ioc\master\%2
    make clean uninstall && make
    popd
) else (
    set ioc_error=CANNOT FIND IOC MODULE
    set /A errors += 1
    echo !ioc_error!
)

echo ERRORS/WARNINGS: !errors! (Note: these are errors in the make_ioc script, not the actual making of the ioc.)
if NOT !support_error! == "" ( echo !support_error! )
if NOT !ioc_error! == "" ( echo !ioc_error! )

endlocal
