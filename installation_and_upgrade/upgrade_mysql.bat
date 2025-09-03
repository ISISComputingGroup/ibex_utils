setlocal EnableDelayedExpansion

call %~dp0run_one_task.bat force_upgrade_mysql
IF %errorlevel% neq 0 EXIT /b %errorlevel%
