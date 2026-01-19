# 🚀 Sprint: LLM-Powered File Processing

**Sprint-Ziel:** Intelligente Dateiverarbeitung mit Gemini AI für das NCA Toolkit

**Dauer:** 6 Tage  
**Start:** 2026-01-06  
**Ende:** 2026-01-12

---

## 📋 Sprint Backlog

### ✅ Phase 1: Foundation (Tag 1-2)
- [x] Architektur-Plan erstellt
- [x] LLM Service implementiert (Gemini 2.0 Flash)
- [x] File Handler implementiert
- [ ] Dependencies installieren
- [ ] Git Repository einrichten
- [ ] Dokumentation erstellen

### 🔄 Phase 2: Integration (Tag 3-4)
- [ ] Flask Backend erweitern
- [ ] File Upload Endpoint
- [ ] LLM-Integration in API
- [ ] Frontend: Drag & Drop UI
- [ ] Frontend: File Preview
- [ ] End-to-End Testing

### 🎯 Phase 3: Polish & Deploy (Tag 5-6)
- [ ] Error Handling verbessern
- [ ] Loading States
- [ ] Result Display
- [ ] Cleanup-Job für alte Dateien
- [ ] Production-Ready Checks
- [ ] Deployment

---

## 🏗️ Architektur

```
User Upload (Drag & Drop)
    ↓
Flask Backend (/api/process)
    ↓
LLM Service (Gemini 2.0 Flash)
    ↓
File Handler (Upload zu /uploads)
    ↓
NCA Toolkit API
    ↓
Result zurück
```

---

## 📁 Projektstruktur

```
MCP-NCA-TOOLKIT/
├── server/
│   ├── app.py                 # Flask Main App
│   ├── llm_service.py         # ✅ Gemini Integration
│   ├── file_handler.py        # ✅ File Upload Logic
│   ├── requirements.txt       # Dependencies
│   ├── .env.example           # Config Template
│   └── README.md              # Backend Docs
│
├── web/
│   ├── index.html             # Frontend
│   ├── styles.css             # Styling
│   └── app.js                 # JavaScript Logic
│
├── uploads/                   # Uploaded Files (gitignored)
├── data/                      # Persistent Data (gitignored)
│
├── docs/
│   ├── ARCHITEKTUR-PLAN.md    # ✅ Architecture
│   ├── SPRINT.md              # ✅ This file
│   └── API.md                 # API Documentation
│
├── .gitignore                 # ✅ Git Ignore Rules
├── docker-compose.yml         # Docker Setup
├── README.md                  # Main Documentation
└── start-server.ps1           # Quick Start Script
```

---

## 🔧 Technologie-Stack

### Backend
- **Flask** 3.0.0 - Web Framework
- **Gemini 2.0 Flash** - LLM für Intent Recognition
- **Werkzeug** - File Handling
- **Requests** - HTTP Client

### Frontend
- **Vanilla JavaScript** - No Framework
- **Drag & Drop API** - File Upload
- **Fetch API** - HTTP Requests

### Infrastructure
- **Docker** - NCA Toolkit Container
- **Python venv** - Virtual Environment
- **Git** - Version Control

---

## 📝 Sprint Tasks

### Tag 1: Setup & Foundation ✅

**Completed:**
- [x] Architektur-Plan erstellt (`ARCHITEKTUR-PLAN.md`)
- [x] LLM Service implementiert (`server/llm_service.py`)
- [x] File Handler implementiert (`server/file_handler.py`)
- [x] .gitignore erstellt
- [x] Sprint-Dokumentation erstellt

**Next:**
- [ ] Dependencies installieren
- [ ] Git Commit erstellen
- [ ] Backend erweitern

---

### Tag 2: Backend Integration

**Tasks:**
- [ ] Flask App erweitern mit:
  - [ ] `/api/process` Endpoint
  - [ ] File Upload Handling
  - [ ] LLM Integration
  - [ ] Error Handling
- [ ] Testing:
  - [ ] File Upload testen
  - [ ] LLM Extraction testen
  - [ ] End-to-End Flow testen

**Acceptance Criteria:**
- ✅ Dateien können hochgeladen werden
- ✅ LLM erkennt Intent korrekt
- ✅ Parameter werden extrahiert
- ✅ NCA API wird aufgerufen

---

### Tag 3: Frontend Development

**Tasks:**
- [ ] Drag & Drop UI implementieren
- [ ] File Preview anzeigen
- [ ] Upload Progress Bar
- [ ] Integration mit Backend
- [ ] Error Messages

**Acceptance Criteria:**
- ✅ Dateien können per Drag & Drop hochgeladen werden
- ✅ Preview wird angezeigt
- ✅ Upload-Status ist sichtbar
- ✅ Fehler werden angezeigt

---

### Tag 4: End-to-End Testing

**Tasks:**
- [ ] Test-Szenarien definieren
- [ ] Manuelle Tests durchführen
- [ ] Bug Fixes
- [ ] Performance Optimierung

**Test-Szenarien:**
1. Video + Audio zusammenfügen
2. Video transkribieren
3. Screenshot erstellen
4. MP3 Konvertierung
5. Fehlerbehandlung

---

### Tag 5: Polish & Documentation

**Tasks:**
- [ ] UI Polish
- [ ] Loading States verbessern
- [ ] Result Display optimieren
- [ ] API Dokumentation
- [ ] User Guide

**Deliverables:**
- [ ] `docs/API.md` - API Dokumentation
- [ ] `docs/USER-GUIDE.md` - Benutzer-Anleitung
- [ ] `README.md` - Updated

---

### Tag 6: Deployment & Cleanup

**Tasks:**
- [ ] Production Config
- [ ] Cleanup-Job implementieren
- [ ] Security Review
- [ ] Final Testing
- [ ] Git Tag erstellen

**Deployment Checklist:**
- [ ] Environment Variables gesetzt
- [ ] Gemini API Key konfiguriert
- [ ] Upload-Ordner erstellt
- [ ] Docker Container läuft
- [ ] Server startet automatisch

---

## 🎯 Definition of Done

Ein Feature ist "Done" wenn:
- ✅ Code implementiert
- ✅ Getestet (manuell)
- ✅ Dokumentiert
- ✅ Git Commit erstellt
- ✅ Funktioniert End-to-End

---

## 📊 Metriken

### Erfolgs-Kriterien:
- **LLM Accuracy**: >90% korrekte Intent-Erkennung
- **Upload Speed**: <5s für 100MB Datei
- **API Response**: <30s für einfache Operationen
- **Error Rate**: <5%

### Kosten:
- **Gemini API**: ~$0.11/Monat (kostenlose Quota)
- **Storage**: ~$0.15/Monat (Cloudflare R2)
- **Total**: ~$0.26/Monat

---

## 🐛 Known Issues

### Docker Container
- ⚠️ Gunicorn Worker crashen gelegentlich
- ⚠️ Health-Check dauert ~30s
- ✅ Workaround: Container neu starten

### LLM
- ⚠️ Benötigt API Key
- ✅ Fallback: Keyword-Matching

---

## 📚 Dokumentation

### Erstellt:
- ✅ `ARCHITEKTUR-PLAN.md` - Vollständige Architektur
- ✅ `SPRINT.md` - Sprint-Dokumentation
- ✅ `server/llm_service.py` - LLM Service mit Docs
- ✅ `server/file_handler.py` - File Handler mit Docs

### TODO:
- [ ] `docs/API.md` - API Dokumentation
- [ ] `docs/USER-GUIDE.md` - Benutzer-Anleitung
- [ ] `README.md` - Main Docs updaten

---

## 🚀 Quick Start

### 1. Dependencies installieren
```powershell
cd server
pip install -r requirements.txt
pip install -r requirements-update.txt
```

### 2. Environment konfigurieren
```powershell
# .env erstellen
Copy-Item .env.example .env

# Gemini API Key eintragen
# GEMINI_API_KEY=your_key_here
```

### 3. Server starten
```powershell
.\start-server.ps1
```

### 4. Testen
```
http://localhost:5000
```

---

## 🔄 Git Workflow

### Commits:
```bash
# Feature implementiert
git add .
git commit -m "feat: LLM service with Gemini integration"

# Bug Fix
git commit -m "fix: file upload size validation"

# Dokumentation
git commit -m "docs: add sprint documentation"
```

### Branches:
- `main` - Production
- `develop` - Development
- `feature/*` - Features
- `bugfix/*` - Bug Fixes

---

## 📞 Support

Bei Fragen:
1. Siehe `ARCHITEKTUR-PLAN.md`
2. Siehe `docs/API.md`
3. GitHub Issues erstellen

---

**Sprint Owner:** AI Assistant  
**Product Owner:** User  
**Start:** 2026-01-06  
**Status:** 🔄 In Progress (Tag 1 abgeschlossen)
