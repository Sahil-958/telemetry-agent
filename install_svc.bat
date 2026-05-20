@echo off
setlocal

:: Get the current directory where the script is located
set "WORK_DIR=%~dp0"
set "VBS_FILE=%WORK_DIR%sys_init.vbs"
set "TASK_NAME=WinSysDiagSvc"

echo Creating system diagnostic task...

:: Create the scheduled task
:: /sc onlogon: Run when the user logs on
:: /tn: Task Name
:: /tr: Task Run (command to execute)
:: /it: Interactive (required for some UI-related captures)
:: /f: Force (overwrite if exists)
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%VBS_FILE%\"" /sc onlogon /it /f

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Task "%TASK_NAME%" created.
    echo The service will now start automatically at every login.
    
    :: Set the restart on failure policy using PowerShell (schtasks alone is limited here)
    powershell -Command "$task = Get-ScheduledTask -TaskName '%TASK_NAME%'; $task.Settings.RestartInterval = 'PT1M'; $task.Settings.RestartCount = 999; Set-ScheduledTask -InputObject $task"
    
    echo Policy updated: Service will restart every 1 minute if it fails.
) else (
    echo.
    echo ERROR: Failed to create task. Make sure you are running as Administrator.
)

pause
