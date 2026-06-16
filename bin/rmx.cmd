@echo off
setlocal
set SCRIPT_DIR=%~dp0

@REM echo Running script: %~f0

python "%SCRIPT_DIR%rmx_poll.py" %*
