set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
call "%~dp0\define_latest_genie_python.bat"
IF %errorlevel% neq 0 EXIT /b %errorlevel%

git --version

IF %errorlevel% neq 0 (
    echo No installation of Git found on machine. Please download Git from https://git-scm.com/downloads before proceeding.
    EXIT /b %errorlevel%
)

call "%LATEST_PYTHON%" "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --release_suffix "%SUFFIX%" --confirm_step truncate_database
IF %errorlevel% neq 0 EXIT /b %errorlevel%
