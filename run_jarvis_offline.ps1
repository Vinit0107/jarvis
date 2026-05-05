$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe"

if (-not (Test-Path $Python)) {
    $Python = "python"
}

Set-Location $ProjectRoot
& $Python "$ProjectRoot\jarvis.py" --voice --recognition offline
