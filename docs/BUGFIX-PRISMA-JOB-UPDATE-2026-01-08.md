# 🐛 Bugfix: Prisma Job Update Fehler

**Datum:** 2026-01-08 17:09  
**Status:** ✅ Behoben

## Problem

**Fehlermeldung in Logs:**
```
2026-01-08 17:08:04 - __main__ - ERROR - 💥 Job 27ef87cf-9eb8-48f7-a983-9e6e14bd2614 failed
Traceback (most recent call last):
  File "C:\CODE\GIT\MCP-NCA-TOOLKIT\server\app.py", line 528, in process_job_async
    db_service.update_job(job_id, {'params': params})
    Field does not exist in enclosing type.
```

## Root Cause

In `server/db_service.py` wurde die `update_job()` Funktion nur `result` als JSON serialisiert, aber **nicht `params`**.

**Prisma Schema:**
```prisma
model Job {
  params    String   // JSON blob - muss String sein!
  result    String?  // JSON blob
}
```

**Problem-Code (app.py:528):**
```python
# params ist ein Dictionary
db_service.update_job(job_id, {'params': params})
```

**Alte update_job Funktion:**
```python
def update_job(job_id, data):
    # Nur result wurde serialisiert ❌
    if 'result' in data and not isinstance(data['result'], str):
        data['result'] = json.dumps(data['result'])
    
    return db.job.update(where={'id': job_id}, data=data)
```

## Lösung

**Neue update_job Funktion:**
```python
def update_job(job_id, data):
    """Updates a job with partial data"""
    # Ensure nested objects like result and params are serialized if passed
    if 'result' in data and not isinstance(data['result'], str):
        data['result'] = json.dumps(data['result'])
    
    if 'params' in data and not isinstance(data['params'], str):
        data['params'] = json.dumps(data['params'])  # ✅ Neu hinzugefügt
    
    return db.job.update(
        where={'id': job_id},
        data=data
    )
```

## Geänderte Dateien

- ✅ `server/db_service.py` - Zeilen 43-55

## Testing

Nach dem Fix sollte:
1. ✅ Job-Updates mit Dictionary-Params funktionieren
2. ✅ Job-Updates mit String-Params weiterhin funktionieren (wird nicht doppelt serialisiert)
3. ✅ Keine Prisma-Fehler mehr in den Logs

## Auswirkung

- **Betroffene Funktionen:** Alle Job-Updates in `process_job_async()`
- **Schweregrad:** Hoch (verhinderte Job-Verarbeitung)
- **Häufigkeit:** Bei jedem Request mit Parameter-Resolution

---

**Behoben durch:** AI Agent  
**Verifiziert:** Pending (Server-Neustart erforderlich)
