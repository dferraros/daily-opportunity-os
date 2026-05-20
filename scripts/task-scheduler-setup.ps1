# Daily Opportunity OS -- Windows Task Scheduler setup
# Run this once from PowerShell (as your normal user, NOT as admin):
#   cd "C:\Users\ferra\OneDrive\Desktop\Projects\.worktrees\daily-opportunity-os"
#   powershell -ExecutionPolicy Bypass -File scripts\task-scheduler-setup.ps1

$TaskName   = "DailyOpportunityOS"
$ProjectRoot = "C:\Users\ferra\OneDrive\Desktop\Projects\.worktrees\daily-opportunity-os"
$BatchFile  = "$ProjectRoot\scripts\run_daily.bat"

Write-Host "Setting up: $TaskName" -ForegroundColor Cyan
Write-Host "  Script: $BatchFile"

if (-not (Test-Path $BatchFile)) {
    Write-Host "ERROR: $BatchFile not found." -ForegroundColor Red
    exit 1
}

# Remove existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task: $TaskName"
}

# Create trigger: daily at 09:00, weekdays only (Mon-Fri)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "09:00"

# Action: cmd.exe /c run_daily.bat (no Git Bash dependency)
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$BatchFile`"" `
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
Write-Host ""
Write-Host "Task registered!" -ForegroundColor Green
Write-Host "  Name:   $TaskName"
Write-Host "  Time:   09:00 Mon-Fri"
Write-Host "  Script: $BatchFile"
Write-Host ""
Write-Host "Test immediately:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "View logs after run:"
Write-Host "  Get-Content `"$ProjectRoot\data\automation_runs.log`" -Tail 50"
Write-Host "  ls `"$ProjectRoot\reports\daily\`""
