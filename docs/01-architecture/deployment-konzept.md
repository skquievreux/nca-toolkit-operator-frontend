# 🏗️ Deployment & Versioning Konzept - NCA Toolkit

**Version:** 1.0.0  
**Datum:** 2026-01-06  
**Status:** Production Ready

---

## 📋 Inhaltsverzeichnis

1. [Versionierung](#versionierung)
2. [Build-Prozess](#build-prozess)
3. [Container-Strategie](#container-strategie)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Deployment-Optionen](#deployment-optionen)
6. [Monitoring & Logging](#monitoring--logging)

---

## 1. Versionierung

### 1.1 Semantic Versioning

Wir nutzen **Semantic Versioning 2.0.0** (wie im Governance-Framework):

```
MAJOR.MINOR.PATCH
  │     │     └─ Bug Fixes, kleine Änderungen
  │     └─────── Neue Features (backwards compatible)
  └───────────── Breaking Changes
```

**Beispiele:**
- `1.0.0` → Initial Release
- `1.1.0` → Neue Features (Drag & Drop, Live-Logs)
- `1.1.1` → Bug Fix
- `2.0.0` → Breaking Change (z.B. neue API-Struktur)

### 1.2 Version-Anzeige

#### Frontend (`web/app.js`)
```javascript
const VERSION = {
    app: '1.0.0',
    build: '2026-01-06T11:30:00Z',
    commit: process.env.GIT_COMMIT || 'dev'
};

console.log(`🚀 NCA Toolkit v${VERSION.app} (Build: ${VERSION.build})`);
```

#### Backend (`server/app.py`)
```python
VERSION = {
    'app': '1.0.0',
    'build': '2026-01-06T11:30:00Z',
    'commit': os.getenv('GIT_COMMIT', 'dev')
}

logger.info(f"🚀 NCA Toolkit Backend v{VERSION['app']}")
logger.info(f"📅 Build: {VERSION['build']}")
logger.info(f"🔖 Commit: {VERSION['commit']}")
```

#### Version-Endpoint
```python
@app.route('/api/version', methods=['GET'])
def get_version():
    return jsonify({
        'version': VERSION['app'],
        'build': VERSION['build'],
        'commit': VERSION['commit'],
        'python': sys.version,
        'dependencies': {
            'flask': flask.__version__,
            'gemini': genai.__version__ if GEMINI_API_KEY else 'not configured'
        }
    })
```

---

## 2. Build-Prozess

### 2.1 Build-Script (`build.ps1`)

```powershell
# Build Script für NCA Toolkit
param(
    [string]$Version = "dev",
    [switch]$Production
)

Write-Host "🏗️ Building NCA Toolkit v$Version" -ForegroundColor Cyan

# 1. Version in Dateien schreiben
$buildTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$gitCommit = git rev-parse --short HEAD

# Frontend Version
$frontendVersion = @"
const VERSION = {
    app: '$Version',
    build: '$buildTime',
    commit: '$gitCommit'
};
export default VERSION;
"@
$frontendVersion | Out-File -FilePath "web/version.js" -Encoding UTF8

# Backend Version
$backendVersion = @"
VERSION = {
    'app': '$Version',
    'build': '$buildTime',
    'commit': '$gitCommit'
}
"@
$backendVersion | Out-File -FilePath "server/version.py" -Encoding UTF8

# 2. Dependencies prüfen
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
cd server
.\venv\Scripts\pip.exe check

# 3. Tests ausführen (wenn vorhanden)
if (Test-Path "tests") {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    .\venv\Scripts\pytest.exe
}

# 4. Production Build
if ($Production) {
    Write-Host "🚀 Creating production build..." -ForegroundColor Green
    
    # Minify Frontend (optional)
    # npm run build
    
    # Create distribution package
    $distPath = "dist/nca-toolkit-$Version"
    New-Item -ItemType Directory -Force -Path $distPath
    
    Copy-Item -Path "web" -Destination "$distPath/web" -Recurse
    Copy-Item -Path "server" -Destination "$distPath/server" -Recurse
    Copy-Item -Path "docker-compose.yml" -Destination "$distPath/"
    Copy-Item -Path "README.md" -Destination "$distPath/"
    
    Write-Host "✅ Build complete: $distPath" -ForegroundColor Green
}

Write-Host "✅ Build finished!" -ForegroundColor Green
```

### 2.2 Automatische Version aus Git

```powershell
# get-version.ps1
$tag = git describe --tags --abbrev=0 2>$null
if ($tag) {
    Write-Output $tag
} else {
    $commit = git rev-parse --short HEAD
    Write-Output "0.0.0-dev+$commit"
}
```

---

## 3. Container-Strategie

### 3.1 Multi-Container Setup

```yaml
# docker-compose.yml (erweitert)
version: '3.8'

services:
  # NCA Toolkit API (existing)
  nca-toolkit:
    image: stephengpope/no-code-architects-toolkit@sha256:19191d643515...
    container_name: nca-toolkit-mcp
    ports:
      - "8080:8080"
    environment:
      - API_KEY=${NCA_API_KEY}
      - LOCAL_STORAGE_PATH=/data
    volumes:
      - ./data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - nca-network

  # Backend Server (NEW!)
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: nca-backend
    ports:
      - "5000:5000"
    environment:
      - NCA_API_URL=http://nca-toolkit:8080
      - NCA_API_KEY=${NCA_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - UPLOAD_FOLDER=/uploads
    volumes:
      - ./uploads:/uploads
      - ./server:/app
    depends_on:
      - nca-toolkit
    restart: unless-stopped
    networks:
      - nca-network

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    container_name: nca-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./web:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - nca-network

networks:
  nca-network:
    driver: bridge

volumes:
  uploads:
  data:
```

### 3.2 Backend Dockerfile

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

LABEL maintainer="NCA Toolkit"
LABEL version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server/ .

# Create uploads directory
RUN mkdir -p /uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["python", "app.py"]
```

### 3.3 Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream backend {
        server backend:5000;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts für lange Requests
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Uploads
        location /uploads/ {
            proxy_pass http://backend;
        }

        # Version Info
        location /version {
            default_type application/json;
            return 200 '{"version":"1.0.0","build":"2026-01-06"}';
        }
    }
}
```

---

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Workflow

```yaml
# .github/workflows/build-and-deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 1. Quality Checks
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd server
          pip install -r requirements.txt
      
      - name: Lint Python
        run: |
          pip install flake8
          flake8 server --max-line-length=120
      
      - name: Type Check
        run: |
          pip install mypy
          mypy server --ignore-missing-imports

  # 2. Build Docker Image
  build:
    needs: quality
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Get version
        id: version
        run: |
          if [[ $GITHUB_REF == refs/tags/* ]]; then
            VERSION=${GITHUB_REF#refs/tags/v}
          else
            VERSION=$(git describe --tags --always)
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.backend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.version.outputs.version }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          labels: |
            org.opencontainers.image.version=${{ steps.version.outputs.version }}
            org.opencontainers.image.created=${{ github.event.head_commit.timestamp }}
            org.opencontainers.image.revision=${{ github.sha }}

  # 3. Release (nur bei Tags)
  release:
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: |
            README.md
            docker-compose.yml
```

---

## 5. Deployment-Optionen

### 5.1 Lokale Entwicklung

```powershell
# Development Mode
docker-compose up -d

# Mit Live-Reload
docker-compose -f docker-compose.dev.yml up
```

### 5.2 Production Deployment

```powershell
# 1. Build Production Images
docker-compose -f docker-compose.prod.yml build

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Health Check
curl http://localhost/api/health
```

### 5.3 Cloud Deployment (Vercel/Railway/Fly.io)

**Vercel (Frontend + Serverless Backend):**
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "web/**",
      "use": "@vercel/static"
    },
    {
      "src": "server/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "server/app.py"
    },
    {
      "src": "/(.*)",
      "dest": "web/$1"
    }
  ]
}
```

---

## 6. Monitoring & Logging

### 6.1 Version-Tracking

```python
# server/app.py
@app.before_request
def log_request_info():
    logger.info(f"📨 {request.method} {request.path}")
    logger.debug(f"Version: {VERSION['app']}")
    logger.debug(f"User-Agent: {request.headers.get('User-Agent')}")

@app.after_request
def log_response_info(response):
    logger.info(f"📤 {response.status_code} {request.path}")
    response.headers['X-App-Version'] = VERSION['app']
    response.headers['X-Build-Time'] = VERSION['build']
    return response
```

### 6.2 Health Checks

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': VERSION,
        'uptime': time.time() - START_TIME,
        'services': {
            'nca_toolkit': check_nca_toolkit(),
            'gemini': 'configured' if GEMINI_API_KEY else 'not configured'
        }
    })
```

---

## 7. Implementierungsplan

### Phase 1: Versionierung (Tag 4)
- [ ] Version-System implementieren
- [ ] Build-Script erstellen
- [ ] Version-Endpoint hinzufügen
- [ ] Frontend Version-Anzeige

### Phase 2: Container (Tag 5)
- [ ] Dockerfile.backend erstellen
- [ ] docker-compose erweitern
- [ ] Nginx Setup
- [ ] Volume-Management

### Phase 3: CI/CD (Tag 6)
- [ ] GitHub Actions Workflow
- [ ] Automated Testing
- [ ] Docker Image Publishing
- [ ] Release Automation

---

## 8. Vorteile dieser Architektur

### ✅ Versionierung
- Klare Nachvollziehbarkeit
- Semantic Versioning
- Git-Integration

### ✅ Container
- Isolation
- Reproduzierbarkeit
- Einfaches Deployment
- Skalierbarkeit

### ✅ CI/CD
- Automatische Builds
- Qualitätssicherung
- Schnelle Releases
- Rollback-Fähigkeit

---

## 9. Kosten-Kalkulation

### Entwicklung (Lokal)
- **Kosten:** $0/Monat
- **Setup:** Docker Desktop (kostenlos)

### Production (Cloud)
- **Vercel:** $0-20/Monat (Hobby/Pro)
- **Railway:** $5-20/Monat
- **Fly.io:** $0-10/Monat
- **DigitalOcean:** $6-12/Monat (Droplet)

**Empfehlung:** Railway ($5/Monat) - Einfach, günstig, gut

---

## 10. Nächste Schritte

**Sofort:**
1. Version-System implementieren
2. Build-Script erstellen
3. Version im Frontend/Backend anzeigen

**Diese Woche:**
4. Dockerfile.backend erstellen
5. docker-compose erweitern
6. Testen

**Nächste Woche:**
7. CI/CD Pipeline
8. Production Deployment
9. Monitoring

---

**Bereit für Production!** 🚀

**Version:** 1.0.0  
**Status:** Ready to Implement  
**Compliance:** ✅ Governance Framework v3.0
