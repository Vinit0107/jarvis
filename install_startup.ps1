$ErrorActionPreference = "Stop"

$TaskName = "Local JARVIS Offline Voice"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunScript = Join-Path $ProjectRoot "run_jarvis_offline.ps1"
$TaskDescription = "Starts local JARVIS in offline voice mode when this Windows user logs in."
$TaskArgs = "-NoExit -ExecutionPolicy Bypass -File `"$RunScript`""
$StartupFolder = [Environment]::GetFolderPath("Startup")
$StartupCmd = Join-Path $StartupFolder "Local JARVIS Offline Voice.cmd"

try {
    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $TaskArgs
    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0)

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description $TaskDescription `
        -Force | Out-Null

    Write-Host "Installed startup task: $TaskName"
} catch {
    $CmdContent = @"
@echo off
cd /d "$ProjectRoot"
powershell.exe -NoExit -ExecutionPolicy Bypass -File "$RunScript"
"@
    Set-Content -Path $StartupCmd -Value $CmdContent -Encoding ASCII
    Write-Host "Task Scheduler was blocked, so installed Startup folder launcher:"
    Write-Host $StartupCmd
}

Write-Host "JARVIS will start in offline voice mode after the next Windows login."
