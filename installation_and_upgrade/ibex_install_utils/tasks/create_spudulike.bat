REM This script activaytes the 'spudulike' user by initiating an action that results in user folder creation.
REM This would be needed on first install of the IBEX application when the user probably doesn't already exist.
REM Once the folder exists, the IBEX start-up script can be copied in to the start-up folder.
REM 
REM This file is part of the ISIS IBEX application.
REM Copyright (C) 2012-2023 Science & Technology Facilities Council.
REM All rights reserved.

REM a trivial action that causes first login activity including folder creattion.
runas /user:spudulike whoami

REM if there was an error, the command window remains open so the user can see what it was.
if %errorlevel% neq 0 exit /B 1

REM iIf no error, just close the comand window.
exit 0
