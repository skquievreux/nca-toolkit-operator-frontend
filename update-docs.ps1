# Update NCA Docs Script
# Holt die neueste Dokumentation vom GitHub Repo

Write-Host "🔄 Updating NCA Documentation..." -ForegroundColor Cyan

$RepoUrl = "https://github.com/stephengpope/no-code-architects-toolkit"
$TempDir = "temp/nca_update"
$TargetDir = "docs/nca-api"

# 1. Clean Temp
if (Test-Path $TempDir) {
    Remove-Item $TempDir -Recurse -Force
}

# 2. Clone (Sparse checkout would be better but simple clone is safest)
Write-Host "📥 Cloning Repository..." -ForegroundColor Yellow
git clone --depth 1 $RepoUrl $TempDir

# 3. Copy Docs
Write-Host "📂 Copying Docs..." -ForegroundColor Yellow
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir
}
Copy-Item -Path "$TempDir/docs/*" -Destination $TargetDir -Recurse -Force

# 4. Clean up
Remove-Item $TempDir -Recurse -Force

Write-Host "✅ Documentation Updated!" -ForegroundColor Green
Write-Host "📍 Location: $TargetDir" -ForegroundColor Cyan
