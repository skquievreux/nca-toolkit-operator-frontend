Write-Host "`n🔄 NCA Toolkit - Job Restart Utility" -ForegroundColor Cyan
Write-Host "====================================`n"

try {
    # Check if server is running
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -ErrorAction Stop
    if ($health.status -ne "healthy") {
        Write-Host "⚠️  Server is reachable but reports unhealthy status." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Server is NOT running! Please start it first with .\start-server.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Triggering retry for failed jobs..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/admin/retry_failed_jobs"
    
    if ($response.count -gt 0) {
        Write-Host "`n✅ Successfully restarted $($response.count) jobs!" -ForegroundColor Green
        Write-Host "Monitor progress in the web UI: http://localhost:5000" -ForegroundColor Cyan
    }
    else {
        Write-Host "`nℹ️  No failed jobs found." -ForegroundColor Gray
    }
}
catch {
    Write-Host "`n❌ Failed to trigger retry: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nPress Enter to exit..."
Read-Host
