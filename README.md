# NCA Toolkit - AI-Powered Media Processing

**Intelligente Medienverarbeitung mit natürlichsprachlicher Steuerung**

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)]()
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)]()
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.0%20Flash-orange.svg)]()

---

## 🎯 Was ist das?

Ein **intelligentes Frontend** für das [No-Code Architects Toolkit](https://github.com/stephengpope/no-code-architects-toolkit) mit:

- 🤖 **AI-Powered Intent Recognition** (Gemini 2.0 Flash)
- 📁 **Drag & Drop File Upload**
- 🎨 **Premium Dark-Mode UI**
- ⚡ **Automatische Parameter-Extraktion**
- 🔄 **Live-Logging & Status-Updates**

**Beispiel:**
```
User: "Füge dieses Video und diese Audiodatei zusammen"
      [Drag & Drop: video.mp4, audio.mp3]

AI:   ✅ Erkannt: Video + Audio zusammenfügen
      ✅ Parameter extrahiert
      ✅ API aufgerufen: /v1/video/add/audio
      ✅ Ergebnis: output.mp4
```

---

## 🚀 Quick Start

### 1. Docker Container starten
```powershell
docker-compose up -d
```

### 2. Python Server starten
```powershell
.\start-server.ps1
```

### 3. Öffnen
```
http://localhost:5000
```

**Das war's!** 🎉

---

## 📋 Voraussetzungen

- ✅ **Docker Desktop** (für NCA Toolkit Container)
- ✅ **Python 3.9+**
- ✅ **Gemini API Key** (kostenlos bei Google AI Studio)

---

## 🏗️ Architektur

```
┌─────────────────────────────────────────┐
│  User (Browser)                          │
│  "Füge Video und Audio zusammen"        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Web Frontend (HTML/JS)                  │
│  • Drag & Drop Upload                    │
│  • Natürlichsprachliche Eingabe         │
└──────────────┬──────────────────────────┘
               │ POST /api/process
               ▼
┌─────────────────────────────────────────┐
│  Flask Backend (Python)                  │
│  ┌─────────────────────────────────┐   │
│  │ LLM Service (Gemini 2.0 Flash)  │   │
│  │ • Intent Recognition             │   │
│  │ • Parameter Extraction           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ File Handler                     │   │
│  │ • Upload Management              │   │
│  │ • URL Generation                 │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ POST /v1/video/add/audio
               ▼
┌─────────────────────────────────────────┐
│  NCA Toolkit API (Docker)                │
│  • Video/Audio Processing                │
│  • FFmpeg Operations                     │
└─────────────────────────────────────────┘
```

---

## 📁 Projektstruktur

```
MCP-NCA-TOOLKIT/
├── server/                 # Flask Backend
│   ├── app.py             # Main Application
│   ├── llm_service.py     # Gemini Integration
│   ├── file_handler.py    # File Upload Logic
│   └── requirements.txt   # Dependencies
│
├── web/                   # Frontend
│   ├── index.html         # UI
│   ├── styles.css         # Premium Dark Mode
│   └── app.js             # JavaScript Logic
│
├── docs/                  # Standardisierte Dokumentation (v3.0)
│   ├── 01-architecture/   # Konzepte & Architektur
│   ├── 02-implementation/ # Setup & Integration
│   ├── 03-operations/     # Betrieb & Maintenance
│   ├── 04-business/       # Berichte & Strategie
│   └── 05-reference/      # API & Referenzen
│
├── uploads/               # Uploaded Files
├── docker-compose.yml     # Docker Setup
└── start-server.ps1       # Quick Start Script
```

---

## 🔧 Installation

### 1. Repository klonen
```powershell
git clone <your-repo-url>
cd MCP-NCA-TOOLKIT
```

### 2. Docker Container starten
```powershell
docker-compose up -d
```

### 3. Python Environment einrichten
```powershell
cd server
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-update.txt
```

### 4. Environment konfigurieren
```powershell
# .env erstellen
Copy-Item .env.example .env

# Bearbeiten und API-Keys eintragen:
# GEMINI_API_KEY=your_gemini_key
# NCA_API_KEY=your_nca_key
```

### 5. Server starten
```powershell
python app.py
```

### 6. Öffnen
```
http://localhost:5000
```

---

## 🎯 Features

### ✅ Implementiert
- 🤖 **LLM-Integration** (Gemini 2.0 Flash)
- 📁 **File Upload System**
- 🎨 **Premium UI** (Dark Mode)
- 📊 **Live-Logging**
- 🔄 **Auto-Reload** (Development)
- ⚡ **Fast Response** (~500ms LLM)

### 🔄 In Entwicklung
- 📤 **Drag & Drop UI**
- 📊 **Progress Bars**
- 🎬 **Result Preview**
- ☁️ **Cloud Storage** (Cloudflare R2)

### 🎯 Geplant
- 🔐 **User Authentication**
- 📈 **Analytics Dashboard**
- 🌐 **Multi-Language Support**
- 📱 **Mobile App**

---

## 💡 Verwendung

### Beispiel 1: Video + Audio zusammenfügen

**Web-Oberfläche:**
1. Öffne http://localhost:5000
2. Drag & Drop: `video.mp4` und `audio.mp3`
3. Schreibe: "Füge diese zusammen"
4. Klicke "Senden"

**Terminal zeigt:**
```
INFO - Proxy Request: /v1/video/add/audio
INFO - LLM detected: Video + Audio merge (confidence: 0.95)
INFO - Calling NCA API...
INFO - Response: {"output_url": "..."}
```

### Beispiel 2: Video transkribieren

**Web-Oberfläche:**
1. Drag & Drop: `video.mp4`
2. Schreibe: "Transkribiere dieses Video auf Deutsch"
3. Klicke "Senden"

**Ergebnis:**
```json
{
  "text": "Transkribierter Text...",
  "language": "de",
  "confidence": 0.98
}
```

---

## 🔐 Sicherheit

### API-Keys
- ✅ Werden in `.env` gespeichert (gitignored)
- ✅ Nie im Code hardcoded
- ✅ Nur Server-seitig verwendet

### File Upload
- ✅ Größen-Limit: 500MB (konfigurierbar)
- ✅ Typ-Validierung
- ✅ Unique Filenames (UUID)
- ✅ Auto-Cleanup nach 24h

### Best Practices
- ✅ CORS konfiguriert
- ✅ Error Handling
- ✅ Input Validation
- ✅ Logging aktiviert

---

## 📊 Performance

### Metriken
- **LLM Response**: ~500ms
- **File Upload**: <5s für 100MB
- **API Call**: <30s für einfache Ops
- **Total**: <1 Min für Standard-Tasks

### Kosten
- **Gemini API**: ~$0.11/Monat (kostenlose Quota: 1500 req/Tag)
- **Storage**: ~$0.15/Monat (Cloudflare R2)
- **Total**: **~$0.26/Monat**

---

## 🐛 Troubleshooting

### Server startet nicht
```powershell
# Python-Version prüfen
python --version  # Sollte 3.9+ sein

# Dependencies neu installieren
pip install -r requirements.txt
```

### Docker Container nicht erreichbar
```powershell
# Container-Status
docker-compose ps

# Logs prüfen
docker-compose logs --tail=50

# Neu starten
docker-compose restart
```

### LLM funktioniert nicht
```powershell
# API-Key prüfen
# In .env: GEMINI_API_KEY=...

# Fallback wird automatisch genutzt
# (Keyword-Matching ohne LLM)
```

---

## 📚 Dokumentation

- **[Architektur-Plan](docs/01-architecture/architektur-plan.md)** - Vollständige Systemarchitektur
- **[Quick Start Guide](docs/02-implementation/quick-start.md)** - Schnelleinstieg
- **[Monitoring-Guide](docs/03-operations/monitoring-guide.md)** - Docker & Debugging
- **[API-Referenz](docs/05-reference/alle-funktionen.md)** - Alle Endpunkte

---

## 🤝 Contributing

### Git Workflow
```bash
# Feature Branch erstellen
git checkout -b feature/my-feature

# Änderungen committen
git add .
git commit -m "feat: add new feature"

# Push
git push origin feature/my-feature

# Pull Request erstellen
```

### Commit Messages
- `feat:` - Neues Feature
- `fix:` - Bug Fix
- `docs:` - Dokumentation
- `style:` - Code-Formatierung
- `refactor:` - Code-Refactoring
- `test:` - Tests
- `chore:` - Maintenance

---

## 📝 Changelog

### [1.0.0] - 2026-01-06

**Added:**
- ✅ LLM Service (Gemini 2.0 Flash)
- ✅ File Handler
- ✅ Flask Backend
- ✅ Premium UI
- ✅ Live-Logging
- ✅ Sprint-Dokumentation

**Changed:**
- ✅ Architektur komplett überarbeitet
- ✅ Von direkten API-Calls zu LLM-basiert

**Fixed:**
- ✅ Docker Container Worker-Probleme dokumentiert
- ✅ Error Handling verbessert

---

## 📞 Support

Bei Fragen oder Problemen:
1. Siehe [Dokumentation](docs/)
2. Prüfe [Known Issues](docs/SPRINT.md#known-issues)
3. Erstelle ein GitHub Issue

---

## 📄 Lizenz

Dieses Projekt nutzt das [No-Code Architects Toolkit](https://github.com/stephengpope/no-code-architects-toolkit).

---

## 🙏 Credits

- **NCA Toolkit**: [stephengpope/no-code-architects-toolkit](https://github.com/stephengpope/no-code-architects-toolkit)
- **Gemini AI**: Google AI Studio
- **Flask**: Pallets Projects
- **Docker**: Docker Inc.

---

**Made with ❤️ and AI**

**Version:** 1.0.0  
**Last Updated:** 2026-01-06  
**Status:** 🚀 Active Development
