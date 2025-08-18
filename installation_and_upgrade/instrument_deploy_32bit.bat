setlocal
call %~dp0instrument_deploy.bat --server_arch x86 %*
IF %errorlevel% neq 0 EXIT /b %errorlevel%
