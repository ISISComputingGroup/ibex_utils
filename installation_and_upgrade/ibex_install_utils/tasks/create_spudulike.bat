REM This script creates the 'spudulike' user, and initiates an action that results in user folder creation.
REM This would be needed on first install of the IBEX application when the user probably doesn't already exist.
REM Once the folder exists, the IBEX start-up script is copied in to the start-up folder.
REM 
REM This file is part of the ISIS IBEX application.
REM Copyright (C) 2012-2023 Science & Technology Facilities Council.
REM All rights reserved.

set SPUDULIKE=spudulike

REM prompt the administrator user for the user password.
set /p "SPUDPASS=enter %SPUDULIKE% password "
set FROM_PATH="%1"
if %FROM_PATH%=="" set FROM_PATH="C:\Instrument\Apps\EPICS\ibex_system_boot.bat"

set USER_FOLDER="C:\Users\%SPUDULIKE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
REM create the user
net user spudulike %SPUDPASS% /add
REM a trivial action that causes first login activity including folder creattion.
runas /user:spudulike whoami
REM copy the stattup file.
xcopy /I %FROM_PATH% %USER_FOLDER%
REM grant read access to administrators so that when the upgrade utilitry is run again, the files and folders will be acessible.
REM this prevents duplicate creation and copying.
icacls "C:\Users\%SPUDULIKE%" /inheritance:e /grant:r "Administrators":R
REM Close only on success - so we can see what failures ocurred.
if %ERRORLEVEL% EQU 0 exit


