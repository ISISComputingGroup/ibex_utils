REM Activate a virtual environment created by set_up_venv.bat. Also set the UV_TEMP_VENV var.
REM this might be needed if ie. stop_ibex_server calls config_env and wipes env vars.
set UV_TEMP_VENV=C:\Instrument\Var\tmp\.deployscriptvenv
call %UV_TEMP_VENV%\scripts\activate
