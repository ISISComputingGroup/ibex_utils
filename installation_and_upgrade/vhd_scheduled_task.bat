REM NOTE: this is a separate task expected to be running as admin via a scheduled task every minute on the machine which builds VHDS.

REM Use a locally installed python in C:\users\<username>\Documents\Python as we don't want to execute code directly from
REM a network share as the admin user.
call "C:\Users\Administrator\Documents\Python\python.exe" "%~dp0vhd_scheduled_task.py"
IF %ERRORLEVEL% neq 0 EXIT /b %errorlevel%
