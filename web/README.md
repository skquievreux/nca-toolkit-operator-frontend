# 🚀 NCA Toolkit AI Assistant - Web Interface

## Übersicht

Eine **intelligente Web-Oberfläche** für das No-Code Architects Toolkit mit natürlichsprachlicher Steuerung. Beschreiben Sie einfach, was Sie tun möchten, und die KI wählt automatisch die richtigen APIs aus!

## ✨ Features

### 🤖 AI-Powered Intent Recognition
- Natürlichsprachliche Eingabe in Deutsch oder Englisch
- Automatische Erkennung der benötigten API-Endpunkte
- Intelligente Parameter-Extraktion aus Ihrer Beschreibung

### 🎯 Unterstützte Aktionen

#### 🎵 Audio
- Audio-Dateien zusammenfügen

#### 💻 Code
- Python-Code remote ausführen

#### 🖼️ Image
- Bilder zu Videos konvertieren
- Webseiten-Screenshots erstellen

#### 📹 Media
- Medienformate konvertieren
- Zu MP3 konvertieren
- Audio/Video transkribieren
- Metadaten extrahieren

#### 🎥 Video
- Audio zu Video hinzufügen
- Untertitel hinzufügen
- Videos zusammenfügen
- Video-Größe ändern
- Und mehr...

### 💡 Intelligente Features

- **Auto-Completion**: Beispiel-Prompts zum Schnellstart
- **File Attachments**: Dateien direkt anhängen
- **History**: Alle Aktionen werden gespeichert
- **Auto-Execute**: Optional automatische Ausführung
- **Real-time Status**: Live-Updates während der Verarbeitung

## 🚀 Schnellstart

### 1. Öffnen Sie die Web-Oberfläche

```powershell
# Im Browser öffnen
start web/index.html
```

Oder doppelklicken Sie auf `index.html`

### 2. Einstellungen konfigurieren

Klicken Sie auf das ⚙️ Icon und setzen Sie:

- **API URL**: `http://localhost:8080` (Standard)
- **API Key**: Ihr API-Key aus `.env`
- **Auto-Execute**: Optional aktivieren für automatische Ausführung

### 3. Loslegen!

Probieren Sie diese Beispiele:

#### Beispiel 1: Video transkribieren
```
Extrahiere das Transkript aus diesem Video:
https://example.com/video.mp4
```

#### Beispiel 2: Screenshot erstellen
```
Mache einen Screenshot von dieser Webseite:
https://github.com
```

#### Beispiel 3: Video und Audio zusammenfügen
```
Füge dieses Video und diese Audiodatei zusammen:
https://example.com/video.mp4
https://example.com/audio.mp3
```

#### Beispiel 4: Zu MP3 konvertieren
```
Konvertiere dieses Video zu MP3:
https://example.com/video.mp4
```

## 🎨 Benutzeroberfläche

### Chat-Interface
- **Natürlichsprachliche Eingabe**: Beschreiben Sie einfach, was Sie wollen
- **Beispiel-Prompts**: Klicken Sie auf Vorschläge zum Schnellstart
- **File Attachments**: 📎 Button zum Anhängen von Dateien

### API-Action Cards
Für jede erkannte Aktion zeigt die KI:
- ⚡ **Endpunkt**: Welche API wird verwendet
- 📋 **Parameter**: Welche Daten werden gesendet
- ▶️ **Ausführen**: Button zum Starten
- ❌ **Abbrechen**: Button zum Abbrechen

### Status-Anzeige
- 🟡 **Pending**: Wird ausgeführt...
- ✅ **Success**: Erfolgreich!
- ❌ **Error**: Fehler aufgetreten

## 🔧 Erweiterte Nutzung

### URL-Erkennung

Die KI erkennt automatisch URLs in Ihrer Nachricht:

```
Transkribiere https://example.com/video.mp4 auf Deutsch
```

### Sprach-Erkennung

Geben Sie die Sprache an:

```
Transkribiere dieses Video auf Englisch
Transkribiere dieses Video auf Deutsch (Standard)
```

### Multiple Files

Fügen Sie mehrere Dateien an oder geben Sie mehrere URLs an:

```
Füge diese Videos zusammen:
https://example.com/video1.mp4
https://example.com/video2.mp4
https://example.com/video3.mp4
```

## 📚 Keyword-Referenz

Die KI erkennt diese Keywords:

### Audio
- `audio`, `zusammenfügen`, `kombinieren`, `merge`

### Code
- `python`, `code`, `ausführen`, `execute`, `script`

### Image
- `bild`, `video`, `konvertieren`, `screenshot`, `webseite`

### Media
- `konvertieren`, `mp3`, `transkript`, `transcribe`, `metadaten`

### Video
- `video`, `audio`, `untertitel`, `captions`, `größe`, `resize`

## 🎯 Tipps & Tricks

### 1. Seien Sie spezifisch
✅ **Gut**: "Extrahiere das Transkript aus diesem Video auf Deutsch"
❌ **Weniger gut**: "Mach was mit dem Video"

### 2. Nutzen Sie URLs
✅ **Gut**: "Screenshot von https://github.com"
❌ **Weniger gut**: "Screenshot von GitHub"

### 3. Kombinieren Sie Aktionen
```
1. Transkribiere dieses Video
2. Konvertiere es zu MP3
3. Erstelle Untertitel
```

### 4. Nutzen Sie den Verlauf
- Klicken Sie auf 🕐 Icon
- Sehen Sie alle vergangenen Aktionen
- Wiederholen Sie erfolgreiche Aktionen

## 🔐 Sicherheit

### Lokale Speicherung
- API-Key wird **nur im Browser** gespeichert (localStorage)
- Keine Daten werden an externe Server gesendet
- Alle Requests gehen direkt an Ihren lokalen NCA Toolkit Container

### Best Practices
1. Ändern Sie den API-Key in `.env`
2. Nutzen Sie HTTPS für Produktion
3. Exponieren Sie den Container nicht ins Internet
4. Nutzen Sie einen Reverse Proxy für externe Zugriffe

## 🛠️ Troubleshooting

### "API Error: 401"
➡️ **Lösung**: API-Key in Einstellungen prüfen

### "API Error: 404"
➡️ **Lösung**: API URL prüfen (sollte `http://localhost:8080` sein)

### "Keine passende Aktion gefunden"
➡️ **Lösung**: 
- Nutzen Sie klarere Keywords
- Prüfen Sie die Beispiele
- Geben Sie URLs direkt an

### Container läuft nicht
➡️ **Lösung**:
```powershell
docker-compose ps
docker-compose up -d
```

## 🎨 Anpassung

### Eigene Keywords hinzufügen

Bearbeiten Sie `app.js` und fügen Sie Keywords hinzu:

```javascript
const API_ENDPOINTS = {
    // ...
    myCustomAction: {
        endpoint: '/v1/custom/action',
        description: 'Meine eigene Aktion',
        keywords: ['custom', 'eigene', 'aktion'],
        params: ['param1', 'param2']
    }
};
```

### Design anpassen

Bearbeiten Sie `styles.css`:

```css
:root {
    --primary: #your-color;
    --bg-primary: #your-bg-color;
}
```

## 📖 Weitere Ressourcen

- **API-Dokumentation**: https://github.com/stephengpope/no-code-architects-toolkit/tree/main/docs
- **Postman Collection**: https://bit.ly/49Gkh61
- **NCA Toolkit GPT**: https://bit.ly/4feDDk4

## 🆘 Support

Bei Fragen oder Problemen:
1. Prüfen Sie die [Dokumentation](../README.md)
2. Öffnen Sie die Browser-Konsole (F12) für Fehler
3. Erstellen Sie ein [GitHub Issue](https://github.com/stephengpope/no-code-architects-toolkit/issues)

---

**Viel Spaß mit dem NCA Toolkit AI Assistant!** 🚀
