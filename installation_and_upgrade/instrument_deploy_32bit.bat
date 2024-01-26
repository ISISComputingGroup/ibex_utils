setlocal
call %~dp0instrument_deploy.bat x86
IF %errorlevel% neq 0 EXIT /b %errorlevel%
