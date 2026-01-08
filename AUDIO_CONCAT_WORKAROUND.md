# Audio Concatenation Workaround Status

## Problem
Der NCA Toolkit Docker-Container (`stephengpope/no-code-architects-toolkit:latest`) hat:
- ✅ `/combine-videos` - Funktioniert für Videos
- ✅ `/media-to-mp3` - Konvertiert einzelne Dateien zu MP3
- ✅ `/audio-mixing` - Mischt Audio mit Video
- ❌ **KEIN** `/concatenate-audio` oder ähnliches für Audio-Verkettung

## Aktueller Fehler
```
Stream specifier '' in filtergraph description [0][1][2]concat=n=3[s0] matches no streams.
```
→ FFmpeg erwartet Video-Streams, bekommt aber nur Audio

## Mögliche Lösungen

### Option 1: FFmpeg Compose Endpoint (Empfohlen)
Der Container könnte einen `/v1/ffmpeg/compose` Endpoint haben, den wir noch nicht getestet haben.

### Option 2: Lokale Verarbeitung im Flask Backend
- Flask Backend lädt die 3 Audio-Dateien herunter
- Nutzt lokales FFmpeg um sie zu verketten
- Lädt das Ergebnis hoch

### Option 3: Workaround mit Video-Container
- Konvertiere Audio zu "stummen Videos" (schwarzer Screen + Audio)
- Nutze `/combine-videos`
- Extrahiere Audio aus dem Ergebnis

## Empfehlung
Ich schlage vor, **Option 2** zu implementieren, da:
1. Wir volle Kontrolle haben
2. Keine Abhängigkeit von undokumentierten Container-Endpoints
3. Schnelle Implementierung möglich

Soll ich das umsetzen?
