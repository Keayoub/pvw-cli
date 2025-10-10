@echo off
REM Release wrapper: prefer pwsh, fallback to powershell
set SCRIPT_DIR=%~dp0
set PS1=%ProgramFiles%\PowerShell\7\pwsh.exe
if exist "%PS1%" (
    "%PS1%" -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%release.ps1" %*
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%release.ps1" %*
)
