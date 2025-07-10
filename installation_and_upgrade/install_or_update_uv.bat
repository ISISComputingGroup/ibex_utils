REM Script to either update uv or install it
uv self update

REM if the above didnt work uv is probably not installed. install it.
if %errorlevel% neq 0 (
    set UV_INSTALL_DIR=C:\Instrument\Apps\uv
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
	set "Path=C:\Instrument\Apps\uv;%Path%"
)

REM set the uv python executable installation directory permanently
setx UV_PYTHON_INSTALL_DIR C:\Instrument\apps\uv\snakes\
setx UV_CACHE_DIR C:\Instrument\Var\uvcache\
