# Daily Opportunity OS -- Windows Task Scheduler setup
# Run this once from PowerShell (as your normal user, NOT as admin):
#   cd "C:\Users\ferra\OneDrive\Desktop\Projects\.worktrees\daily-opportunity-os"
#   powershell -ExecutionPolicy Bypass -File scripts\task-scheduler-setup.ps1

$TaskName = "DailyOpportunityOS"
$ProjectRoot = "C:\Users\ferra\OneDrive\Desktop\Projects\.worktrees\daily-opportunity-os"
$ScriptPath = "$ProjectRoot\scripts\run_daily.sh"

# Find git bash (standard Git for Windows install location)
$BashPaths = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe"
)
$BashExe = $BashPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $BashExe) {
    Write-Host "ERROR: Git Bash not found. Install Git for Windows first." -ForegroundColor Red
    Write-Host "       Download: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using bash: $BashExe"

# Remove existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task: $TaskName"
}

# Create trigger: daily at 09:00, weekdays only (Mon-Fri)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "09:00"

# Action: bash scripts/run_daily.sh
$Action = New-ScheduledTaskAction `
    -Execute $BashExe `
    -Argument "`"$($ScriptPath.Replace('\', '/'))`"" `
    -WorkingDirectory $ProjectRoot

# Settings: run even if on battery, don't stop if idle, 30min timeout
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -DisallowStartIfOnBatteries $false `
    -StopIfGoingOnBatteries $false `
    -StartWhenAvailable

# Principal: run as current user, only when logged in
$Principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Daily Opportunity OS scout -- runs signal-harvester + scoring + reports at 09:00 Mon-Fri" `
    -Force

Write-Host ""
Write-Host "Task registered successfully!" -ForegroundColor Green
Write-Host "  Name:    $TaskName"
Write-Host "  Time:    09:00 Mon-Fri"
Write-Host "  Script:  $ScriptPath"
Write-Host ""
Write-Host "To test immediately:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "To view logs after run:"
Write-Host "  ls `"$ProjectRoot\reports\daily\`""
