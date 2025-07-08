REM sets up temporary virtual environment for deployment.

set UV_TEMP_VENV=%TEMP%\.deployvenv
set UV_PYTHON=3.12
REM use the on-disk location as we'll be using a venv anyway so it won't dirty the install
uv venv %UV_TEMP_VENV%
%UV_TEMP_VENV%\scripts\activate
