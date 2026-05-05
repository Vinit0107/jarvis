$ErrorActionPreference = "Stop"

$TaskName = "Local JARVIS Offline Voice"
$StartupFolder = [Environment]::GetFolderPath("Startup")
$StartupCmd = Join-Path $StartupFolder "Local JARVIS Offline Voice.cmd"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed startup task: $TaskName"
} else {
    Write-Host "Startup task was not installed: $TaskName"
}

if (Test-Path $StartupCmd) {
    Remove-Item -LiteralPath $StartupCmd -Force
    Write-Host "Removed Startup folder launcher: $StartupCmd"
}
