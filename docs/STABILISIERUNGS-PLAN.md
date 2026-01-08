# 🎯 NCA Toolkit Stabilisierungs-Plan

**Datum:** 2026-01-08  
**Status:** In Planung  
**Ziel:** Stabiles, zuverlässiges System für alle 15+ API-Endpunkte

---

## 📊 Aktuelle Situation

### ✅ Was funktioniert
- Server startet (Flask läuft)
- Logging-System implementiert
- Datenbank-Verbindung (Prisma)
- File-Upload-Mechanismus
- Frontend (Web-Interface)

### ❌ Was NICHT funktioniert
- **Prisma Job Updates** - Serialisierungs-Fehler bei params/result
- **API-Endpunkt-Aufrufe** - Inkonsistente Parameter-Übergabe
- **LLM Intent-Erkennung** - Unzuverlässig ohne GEMINI_API_KEY
- **Error Handling** - Fehler werden nicht sauber abgefangen
- **Testing** - Keine automatisierten Tests für Endpunkte

### 🔢 Verfügbare Endpunkte (15+)

**Aktuell definiert in `app.py`:**
1. `/v1/audio/concatenate` - Audio zusammenfügen
2. `/v1/code/execute/python` - Python ausführen
3. `/v1/image/convert/video` - Bild zu Video
4. `/v1/image/screenshot/webpage` - Screenshot
5. `/v1/media/convert` - Format-Konvertierung
6. `/v1/media/convert/mp3` - MP3-Konvertierung
7. `/v1/media/transcribe` - Transkription
8. `/v1/media/metadata` - Metadaten
9. `/v1/video/add/audio` - Audio zu Video
10. `/v1/video/concatenate` - Videos zusammenfügen
11. `/v1/video/caption` - Untertitel
12. `/v1/video/thumbnail` - Thumbnail
13. `/v1/toolkit/test` - Test
14. `/v1/toolkit/authenticate` - Auth-Test

**Plus lokale Overrides:**
- Screenshot (Selenium)
- Thumbnail (FFmpeg)
- Audio Concat (FFmpeg)
- Video/Audio Mixing (FFmpeg)

---

## 🎯 Strategischer Plan (3 Phasen)

### **Phase 1: Kritische Bugs beheben** (Priorität: HOCH)
**Ziel:** System grundlegend funktionsfähig machen  
**Dauer:** 1-2 Stunden

#### 1.1 Prisma Serialisierung komplett fixen
**Problem:** Jobs schlagen fehl wegen falscher Datentypen

**Lösung:**
```python
# Zentrale Serialisierungs-Funktion
def serialize_job_data(data):
    """Serialisiert alle komplexen Datentypen für Prisma"""
    result = {}
    for key, value in data.items():
        if key in ['params', 'result'] and not isinstance(value, str):
            result[key] = json.dumps(value) if value else None
        else:
            result[key] = value
    return result

# Wrapper für alle update_job Aufrufe
def safe_update_job(job_id, data):
    return db_service.update_job(job_id, serialize_job_data(data))
```

**Änderungen:**
- [ ] Neue Funktion in `db_service.py`
- [ ] Alle `db_service.update_job()` Aufrufe ersetzen
- [ ] Unit-Tests für Serialisierung

#### 1.2 Error Handling standardisieren
**Problem:** Fehler crashen Jobs, keine sauberen Fehlermeldungen

**Lösung:**
```python
def safe_api_call(endpoint, params):
    """Wrapper für alle NCA API Calls mit Error Handling"""
    try:
        response = call_nca_api(endpoint, params)
        return {'success': True, 'data': response}
    except requests.Timeout:
        return {'success': False, 'error': 'Timeout', 'retry': True}
    except requests.ConnectionError:
        return {'success': False, 'error': 'Connection failed', 'retry': True}
    except Exception as e:
        logger.exception(f"API call failed: {endpoint}")
        return {'success': False, 'error': str(e), 'retry': False}
```

**Änderungen:**
- [ ] Wrapper-Funktion erstellen
- [ ] Alle API-Calls umschließen
- [ ] Retry-Logik implementieren

#### 1.3 Fallback-System für LLM
**Problem:** Ohne GEMINI_API_KEY ist Intent-Erkennung unzuverlässig

**Lösung:**
- [ ] Verbesserte Keyword-Matching-Logik
- [ ] Regel-basiertes System für häufige Anfragen
- [ ] User-Feedback bei unsicherer Erkennung

---

### **Phase 2: Endpunkt-Validierung** (Priorität: MITTEL)
**Ziel:** Alle 15 Endpunkte einzeln testen und dokumentieren  
**Dauer:** 2-3 Stunden

#### 2.1 Endpunkt-Test-Suite erstellen

**Struktur:**
```python
# tests/test_endpoints.py
class EndpointTests:
    def test_audio_concatenate(self):
        """Test: Audio-Dateien zusammenfügen"""
        params = {
            'audio_urls': [
                'http://localhost:5000/uploads/test1.mp3',
                'http://localhost:5000/uploads/test2.mp3'
            ]
        }
        result = call_endpoint('/v1/audio/concatenate', params)
        assert result['success'] == True
        assert 'output_url' in result
    
    # ... für alle 15 Endpunkte
```

**Änderungen:**
- [ ] Test-Dateien vorbereiten (Audio, Video, Bild)
- [ ] Test-Suite schreiben
- [ ] Automatisierte Tests ausführen
- [ ] Fehler dokumentieren

#### 2.2 Endpunkt-Dokumentation

**Für jeden Endpunkt:**
```markdown
## /v1/audio/concatenate

**Beschreibung:** Fügt mehrere Audiodateien zusammen

**Parameter:**
- `audio_urls` (array, required) - Liste von Audio-URLs
- `output_format` (string, optional) - Format (default: mp3)

**Beispiel:**
```json
{
  "audio_urls": ["url1", "url2"],
  "output_format": "mp3"
}
```

**Response:**
```json
{
  "success": true,
  "output_url": "http://...",
  "duration": 120
}
```

**Fehler:**
- 400: Fehlende Parameter
- 500: Verarbeitungsfehler
- 504: Timeout
```

**Änderungen:**
- [ ] Dokumentation für alle 15 Endpunkte
- [ ] Beispiele mit echten Daten
- [ ] Fehler-Szenarien dokumentieren

---

### **Phase 3: Robustheit & Monitoring** (Priorität: NIEDRIG)
**Ziel:** Langfristige Stabilität sicherstellen  
**Dauer:** 1-2 Stunden

#### 3.1 Health-Check-System

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    """Umfassender Health-Check"""
    checks = {
        'database': check_database(),
        'nca_api': check_nca_api(),
        'ffmpeg': check_ffmpeg(),
        'disk_space': check_disk_space(),
        'upload_folder': check_upload_folder()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }), status_code
```

#### 3.2 Job-Monitoring Dashboard

**Features:**
- Übersicht aller Jobs (Running, Completed, Failed)
- Fehlerrate pro Endpunkt
- Durchschnittliche Verarbeitungszeit
- Retry-Statistiken

#### 3.3 Automatische Wiederherstellung

```python
# Retry-Mechanismus für fehlgeschlagene Jobs
def retry_failed_jobs():
    """Versucht fehlgeschlagene Jobs erneut"""
    failed_jobs = db_service.get_jobs_by_status('failed')
    
    for job in failed_jobs:
        if job.retry_count < 3:
            logger.info(f"Retrying job {job.id}")
            # Job erneut ausführen
            execute_job(job.id)
```

---

## 📋 Implementierungs-Reihenfolge

### Sofort (Heute)
1. ✅ Prisma Serialisierung komplett fixen
2. ✅ Error Handling für API-Calls
3. ✅ Server-Neustart testen

### Morgen
4. ⏳ Test-Suite für Top 5 Endpunkte
5. ⏳ Dokumentation für Top 5 Endpunkte
6. ⏳ Fallback-LLM verbessern

### Diese Woche
7. ⏳ Alle 15 Endpunkte testen
8. ⏳ Vollständige Dokumentation
9. ⏳ Health-Check implementieren
10. ⏳ Monitoring-Dashboard

---

## 🎯 Erfolgskriterien

### Minimum Viable Product (MVP)
- [ ] **Alle 15 Endpunkte funktionieren** (mindestens mit Beispieldaten)
- [ ] **Keine Prisma-Fehler** mehr
- [ ] **Error Handling** fängt alle Fehler ab
- [ ] **Jobs werden korrekt gespeichert** und angezeigt
- [ ] **Dokumentation** für jeden Endpunkt

### Nice-to-Have
- [ ] Automatische Tests für alle Endpunkte
- [ ] Retry-Mechanismus für fehlgeschlagene Jobs
- [ ] Health-Check-Dashboard
- [ ] Performance-Monitoring

---

## 🔧 Technische Schulden

### Bekannte Probleme
1. **Pydantic V2 Migration** - Teilweise noch alte API
2. **Logging** - Zu verbose in manchen Bereichen
3. **Code-Duplikation** - Viele ähnliche API-Call-Patterns
4. **Fehlende Type Hints** - Nicht überall typisiert
5. **Keine Integration Tests** - Nur manuelle Tests

### Refactoring-Kandidaten
- `call_nca_api()` - Zu komplex, sollte aufgeteilt werden
- `process_job_async()` - Zu lang (>100 Zeilen)
- Parameter-Resolution - Sollte eigene Funktion sein

---

## 📊 Metriken

### Vor Stabilisierung
- **Erfolgsrate:** ~30-40% (geschätzt)
- **Fehlerrate:** ~60-70%
- **Durchschnittliche Job-Dauer:** Unbekannt
- **Logs pro Stunde:** ~5-10 MB

### Nach Stabilisierung (Ziel)
- **Erfolgsrate:** >90%
- **Fehlerrate:** <10%
- **Durchschnittliche Job-Dauer:** Gemessen und dokumentiert
- **Logs pro Stunde:** <500 KB

---

## 🚀 Nächste Schritte

### Jetzt sofort
1. **Prisma-Fix finalisieren** - serialize_job_data() Funktion
2. **Error-Handling-Wrapper** - safe_api_call() Funktion
3. **Server neu starten** - Änderungen testen

### In 30 Minuten
4. **Test-Dateien vorbereiten** - Audio, Video, Bild-Samples
5. **Ersten Endpunkt testen** - /v1/toolkit/test
6. **Dokumentation starten** - Template erstellen

---

**Verantwortlich:** AI Agent  
**Review:** User  
**Nächstes Update:** Nach Phase 1 (in ~1 Stunde)
