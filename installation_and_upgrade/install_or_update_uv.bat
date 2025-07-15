REM Script to either update uv or install it

mkdir c:\Instrument\Apps\uv
xcopy /Y /I \\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\uv\uv-x86_64-pc-windows-msvc\uv.exe c:\Instrument\Apps\uv\
xcopy /Y /I \\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\uv\uv-x86_64-pc-windows-msvc\uvw.exe c:\Instrument\Apps\uv\
xcopy /Y /I \\isis.cclrc.ac.uk\inst$\Kits$\CompGroup\ICP\uv\uv-x86_64-pc-windows-msvc\uvx.exe c:\Instrument\Apps\uv\
set "Path=C:\Instrument\Apps\uv;%Path%"

REM set the uv python executable installation directory permanently
setx UV_PYTHON_INSTALL_DIR C:\Instrument\apps\uv\snakes\
setx UV_CACHE_DIR C:\Instrument\Var\uvcache\
