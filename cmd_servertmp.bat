@echo off
start python -B %~dp0\server_process\main.py 1000 1
start python -B %~dp0\server_process\main.py 0 1
REM pause
exit