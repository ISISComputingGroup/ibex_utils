REM Script to either update uv or install it

robocopy \\isis\inst$\Kits$\CompGroup\ICP\uv\uv-x86_64-pc-windows-msvc c:\Instrument\Apps\uv -MIR -NFL -NDL -NP -R:1 -MT -L
set "Path=C:\Instrument\Apps\uv;%Path%"

REM set the uv python executable installation directory permanently
setx UV_PYTHON_INSTALL_DIR C:\Instrument\apps\uv\snakes\
setx UV_CACHE_DIR C:\Instrument\Var\uvcache\
