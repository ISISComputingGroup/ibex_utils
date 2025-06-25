REM either update uv or install it
uv self update
if %errorlevel% neq 0 (
    powershell -ExecutionPolicy ByPass %~dp0\installuv.ps1
)
REM create temporary virtual environment
set UV_TEMP_VENV=C:\ibex_upgrade_venv
set UV_PYTHON=3.12
REM use the on-disk location as we'll be using a venv anyway so it won't dirty the install
set UV_PYTHON_INSTALL_DIR=C:\Instrument\apps\uv\snakes\
uv venv %UV_TEMP_VENV%
%UV_TEMP_VENV%\scripts\activate
uv pip install -r %~dp0\requirements.txt
