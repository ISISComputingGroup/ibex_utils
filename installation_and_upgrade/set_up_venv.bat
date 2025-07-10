REM sets up temporary virtual environment for deployment and installs requirements.

set UV_TEMP_VENV=C:\Instrument\Var\tmp\.deployscriptvenv
set UV_PYTHON=3.12
REM use the on-disk location as we'll be using a venv anyway so it won't dirty the install
uv venv "%UV_TEMP_VENV%"
call "%UV_TEMP_VENV%\scripts\activate"
uv pip install -r "%~dp0\requirements.txt" --no-build
