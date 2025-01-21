setlocal
set "BACKUPROOT=\\isis.cclrc.ac.uk\inst$\Backups$\stage-deleted\%COMPUTERNAME%"
if not exist "%BACKUPROOT%" mkdir "%BACKUPROOT%"
cd /d C:\Data\old
for /D %%i in ( "ibex_backup_*" ) do (
    @echo Moving %%i
    robocopy "%%i" "\\isis.cclrc.ac.uk\inst$\Backups$\stage-deleted\%COMPUTERNAME%\%%i" /XJ /E /Z /MOVE /NP /NFL /NDL
)
pause
