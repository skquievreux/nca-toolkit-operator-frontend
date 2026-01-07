# System Update Script
# Aktualisiert Docker Images und Dokumentation

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔄 SYSTEM UPDATE                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Update Docs
.\update-docs.ps1

# 2. Update Docker Images
Write-Host "`n🐳 Updating Docker Images..." -ForegroundColor Yellow
docker-compose pull

# 3. Restart Containers
Write-Host "`n🔄 Restarting Containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`n✅ Update Complete!" -ForegroundColor Green
Write-Host "Your system is now running the latest version of NCA Toolkit." -ForegroundColor Cyan
