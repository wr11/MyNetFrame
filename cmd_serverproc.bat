
set SHELL=ConEmu64.exe
set CMD=python
set PATH=%~dp0\server_process\main.py
where %SHELL%
if "%ERRORLEVEL%" == "0" (
	start %SHELL%^
		"%CMD% -B %PATH% 1000 1"^
		"%CMD% -B %PATH% 0 1"

) else (
	start %CMD% -B %PATH% 1000 1
	start %CMD% -B %PATH% 0 1
)
pause
exit