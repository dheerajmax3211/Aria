# ARIA — Windows Task Scheduler Auto-Start
# Run this PowerShell script AS ADMINISTRATOR to set up ARIA to start on login.

$ariaDir = "D:\Projects\Jarvis"
$pythonExe = "C:\Users\dheer\AppData\Local\Programs\Python\Python311\python.exe"
$taskName = "ARIA-AI-Assistant"

$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "-m jarvis.main" `
    -WorkingDirectory $ariaDir

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "ARIA AI Assistant — Voice-first personal AI system" `
    -Force

Write-Host "Task '$taskName' registered. ARIA will start on next login."
Write-Host "To start now: Start-ScheduledTask -TaskName '$taskName'"
Write-Host "To remove: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
