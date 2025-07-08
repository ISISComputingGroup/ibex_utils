setlocal EnableDelayedExpansion

  REM TODO is this just for EPICS_CA_ADDR_LIST? need to get this right...
@REM   call C:\Instrument\Apps\EPICS\config_env.bat
  set EPICS_CA_AUTO_ADDR_LIST=NO
  set EPICS_CA_ADDR_LIST=127.255.255.255 130.246.51.255

call "%~dp0install_or_update_uv.bat"

REM create temporary virtual environment
set UV_TEMP_VENV=%~dp0.venv
set UV_PYTHON=3.12
REM use the on-disk location as we'll be using a venv anyway so it won't dirty the install
uv venv %UV_TEMP_VENV%
call %UV_TEMP_VENV%\scripts\activate

call uv pip install -r %~dp0\requirements.txt --no-build

set "SOURCE=\\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\Releases"
python "%~dp0IBEX_upgrade.py" --release_dir "%SOURCE%" --confirm_step save_motor_params

IF %errorlevel% neq 0 goto ERROR

