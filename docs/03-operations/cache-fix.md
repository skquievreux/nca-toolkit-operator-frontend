# Browser-Cache Problem beheben

## Problem
Der Browser lädt die alte Version von `index.html` und `job-queue.js`, obwohl die Dateien aktualisiert wurden.

## Lösung

### Option 1: Cache in Chrome komplett löschen
1. Drücken Sie `Strg + Shift + Delete`
2. Wählen Sie "Gesamte Zeit"
3. Aktivieren Sie "Bilder und Dateien im Cache"
4. Klicken Sie auf "Daten löschen"
5. Laden Sie `http://localhost:5000` neu

### Option 2: Inkognito-Fenster
1. Drücken Sie `Strg + Shift + N`
2. Öffnen Sie `http://localhost:5000`
3. Die Jobs sollten jetzt sichtbar sein

### Option 3: Version-Parameter erhöhen
Die HTML-Datei verwendet `?v=8` für alle Scripts. Wir können das auf `?v=9` erhöhen.

## Verifikation
Nach dem Cache-Löschen sollten Sie in den DevTools (F12) **KEINE** Fehler mehr sehen:
- ✅ Kein `state is not defined` Fehler
- ✅ Jobs werden in der linken Sidebar angezeigt
- ✅ "Ergebnis anzeigen" Button funktioniert
