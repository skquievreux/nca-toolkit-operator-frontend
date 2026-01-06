# NCA Toolkit MCP Server Wrapper
# Dieses Skript fungiert als Bridge zwischen MCP-Clients und der NCA Toolkit API

param(
    [string]$ApiKey = $env:API_KEY,
    [string]$ApiBase = "http://localhost:8080"
)

# Fallback auf .env Datei
if (-not $ApiKey) {
    $envFile = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^API_KEY=(.+)$') {
                $ApiKey = $matches[1]
            }
        }
    }
}

# Validierung
if (-not $ApiKey) {
    Write-Error "API_KEY nicht gefunden. Setzen Sie die Umgebungsvariable oder .env Datei."
    exit 1
}

# Lese JSON-Input von stdin
$inputJson = [Console]::In.ReadToEnd()

if (-not $inputJson) {
    Write-Error "Kein Input erhalten"
    exit 1
}

try {
    # Parse Request
    $request = $inputJson | ConvertFrom-Json
    
    # Extrahiere Endpoint und Body
    $endpoint = $request.endpoint
    $body = $request.body
    
    # Validierung
    if (-not $endpoint) {
        throw "Endpoint fehlt im Request"
    }
    
    # Erstelle Headers
    $headers = @{
        "x-api-key" = $ApiKey
        "Content-Type" = "application/json"
    }
    
    # Erstelle vollständige URL
    $url = "$ApiBase$endpoint"
    
    # Sende Request an NCA Toolkit API
    $bodyJson = $body | ConvertTo-Json -Depth 10 -Compress
    
    $response = Invoke-RestMethod `
        -Uri $url `
        -Method POST `
        -Headers $headers `
        -Body $bodyJson `
        -ErrorAction Stop
    
    # Rückgabe als JSON
    $response | ConvertTo-Json -Depth 10 -Compress
    
} catch {
    # Fehlerbehandlung
    $errorResponse = @{
        error = $_.Exception.Message
        status = "failed"
        timestamp = (Get-Date).ToString("o")
    }
    
    $errorResponse | ConvertTo-Json -Compress
    exit 1
}
