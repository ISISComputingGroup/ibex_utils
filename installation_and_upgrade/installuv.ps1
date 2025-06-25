powershell -ExecutionPolicy ByPass -c {$env:UV_INSTALL_DIR = "C:\Instrument\Apps\uv";irm https://astral.sh/uv/install.ps1 | iex}
