# 📋 Logging Guide - NCA Toolkit

## Übersicht

Das NCA Toolkit verwendet ein professionelles Logging-System mit automatischer Rotation und konfigurierbaren Log-Levels.

## Konfiguration

### Environment Variables

```bash
# .env Datei
LOG_LEVEL=WARNING    # DEBUG, INFO, WARNING, ERROR, CRITICAL
DEBUG=false          # true für verbose Logging
```

### Log-Levels

| Level        | Beschreibung     | Verwendung                  |
| ------------ | ---------------- | --------------------------- |
| **DEBUG**    | Sehr detailliert | Entwicklung, Fehlersuche    |
| **INFO**     | Informativ       | Wichtige Events             |
| **WARNING**  | Warnungen        | **Standard für Production** |
| **ERROR**    | Fehler           | Fehlerhafte Operationen     |
| **CRITICAL** | Kritisch         | Systemfehler                |

## Log-Dateien

### Production Mode (DEBUG=false)
```
logs/
├── nca-server.log       # Warnings & Errors (max 10MB, 5 Backups)
└── nca-server.log.1     # Rotierte Backups
```

### Debug Mode (DEBUG=true)
```
logs/
├── nca-server.log       # Warnings & Errors
├── debug.log            # ALLE Logs inkl. DEBUG (max 50MB, 3 Backups)
└── debug.log.1          # Rotierte Debug-Backups
```

## Log-Rotation

- **Automatisch**: Logs werden rotiert wenn Größenlimit erreicht
- **Production**: 10 MB pro Datei, 5 Backups (max 50 MB total)
- **Debug**: 50 MB pro Datei, 3 Backups (max 150 MB total)
- **Cleanup**: Logs älter als 30 Tage werden automatisch gelöscht

## Verwendung im Code

```python
from logging_config import get_logger

logger = get_logger(__name__)

# Verschiedene Log-Levels
logger.debug("Detaillierte Debug-Info")      # Nur in DEBUG-Mode
logger.info("Wichtiges Event")                # Nur in INFO-Mode
logger.warning("Warnung - etwas ist unklar")  # Immer geloggt
logger.error("Fehler aufgetreten")            # Immer geloggt
logger.exception("Fehler mit Stacktrace")     # Immer geloggt
```

## Best Practices

### ✅ DO

```python
# Errors immer loggen
logger.error(f"API call failed: {endpoint}")

# Warnings für unerwartete Situationen
logger.warning(f"Cache miss for {key}")

# Debug für Entwicklung
logger.debug(f"Processing params: {params}")
```

### ❌ DON'T

```python
# Keine sensiblen Daten loggen
logger.info(f"API Key: {api_key}")  # ❌

# Keine exzessiven Logs in Loops
for item in large_list:
    logger.info(f"Processing {item}")  # ❌ Use DEBUG

# Keine riesigen Payloads
logger.info(f"Response: {huge_json}")  # ❌ Truncate or use DEBUG
```

## Troubleshooting

### Problem: Logs werden nicht geschrieben

**Lösung:**
```bash
# Prüfe ob logs/ Verzeichnis existiert
mkdir logs

# Prüfe Schreibrechte
chmod 755 logs
```

### Problem: Zu viele Logs

**Lösung:**
```bash
# Erhöhe LOG_LEVEL
LOG_LEVEL=ERROR

# Deaktiviere Debug-Mode
DEBUG=false
```

### Problem: Logs füllen Festplatte

**Lösung:**
- Log-Rotation ist automatisch aktiv
- Alte Logs werden nach 30 Tagen gelöscht
- Manuelles Cleanup: `rm logs/*.log.*`

## Monitoring

### Live-Logs ansehen

```bash
# Alle Logs (Production)
tail -f logs/nca-server.log

# Debug-Logs
tail -f logs/debug.log

# Nur Errors
tail -f logs/nca-server.log | grep ERROR
```

### Log-Statistiken

```bash
# Anzahl Errors heute
grep "$(date +%Y-%m-%d)" logs/nca-server.log | grep ERROR | wc -l

# Häufigste Fehler
grep ERROR logs/nca-server.log | sort | uniq -c | sort -rn | head -10
```

## Migration von altem System

### Vorher (basicConfig)
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Nachher (logging_config)
```python
from logging_config import setup_logging, get_logger

setup_logging()  # Einmal beim App-Start
logger = get_logger(__name__)
```

## Performance

- **Log-Rotation**: Keine Performance-Einbußen
- **DEBUG-Mode**: ~5-10% langsamer (wegen I/O)
- **Production-Mode**: Minimaler Overhead

## Empfehlungen

### Development
```bash
LOG_LEVEL=DEBUG
DEBUG=true
```

### Staging
```bash
LOG_LEVEL=INFO
DEBUG=false
```

### Production
```bash
LOG_LEVEL=WARNING
DEBUG=false
```

## Support

Bei Fragen oder Problemen:
1. Prüfe `logs/nca-server.log` für Errors
2. Aktiviere DEBUG-Mode für Details
3. Siehe Dokumentation: `docs/TROUBLESHOOTING.md`

---

**Letzte Aktualisierung:** 2026-01-08  
**Version:** 1.0.0
