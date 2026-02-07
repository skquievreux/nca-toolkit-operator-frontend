---
title: "n8n Integration für NCA Toolkit"
type: "implementation"
status: "approved"
last_updated: "2026-02-07"
---

# n8n Integration für NCA Toolkit

Diese Anleitung beschreibt, wie Sie das **NCA Toolkit** in **n8n** integrieren.

## Voraussetzungen

- n8n ist installiert und läuft (Lokal oder Cloud).
- NCA Toolkit Container läuft (`http://localhost:8080`).
- Der Container muss für n8n erreichbar sein (bei n8n in Docker ggf. `host.docker.internal` nutzen).

## Methode 1: OpenAPI Import (Empfohlen)

Das NCA Toolkit stellt eine OpenAPI (Swagger) Spezifikation bereit, die n8n direkt importieren kann.

1.  Öffnen Sie Ihren n8n Workflow.
2.  Fügen Sie einen neuen Node hinzu (+).
3.  Suchen Sie nach **"OpenAPI"** oder **"Swagger"** (falls verfügbar, sonst nutzen Sie Methode 2).
    *Hinweis: n8n hat keine native "Import Swagger to Nodes" Funktion zur Laufzeit, aber Sie können HTTP-Requests basierend auf der Spec bauen.*

*Da n8n aktuell keinen direkten "One-Click Import" für dynamische APIs hat, nutzen wir den **HTTP Request Node**.*

## Methode 2: HTTP Request Node

Dies ist der Standardweg für jede Interaktion mit dem NCA Toolkit in n8n.

### Schritt 1: Node hinzufügen
- Fügen Sie einen **HTTP Request** Node hinzu.

### Schritt 2: Konfiguration
Konfigurieren Sie den Node wie folgt:

- **Method**: `POST`
- **URL**: `http://localhost:8080/v1/media/transcribe` (oder anderer Endpunkt)
- **Authentication**: `Generic Credential Type` -> `Header Auth`

### Schritt 3: Auth Credential erstellen
Erstellen Sie ein neues Header Auth Credential:
- **Name**: `x-api-key`
- **Value**: `change_me_to_secure_key_123` (siehe Ihre `.env` Datei)

### Schritt 4: Body Parameter
Wählen Sie unter **Body Parameters** -> **Send Body**: `true`:
- **Content Type**: `JSON`
- **Body**:

```json
{
  "media_url": "https://example.com/video.mp4",
  "language": "de"
}
```

## Übersicht der wichtigsten Endpunkte für n8n

Hier sind die wichtigsten Endpunkte für Ihre Workflows:

| Funktion            | Methode | Endpunkt                  | Body JSON                                    |
| ------------------- | ------- | ------------------------- | -------------------------------------------- |
| **Python Code**     | POST    | `/v1/code/execute/python` | `{ "code": "print('Hello')" }`               |
| **Transkription**   | POST    | `/v1/media/transcribe`    | `{ "media_url": "...", "language": "de" }`   |
| **Bilder zu Video** | POST    | `/v1/image/convert/video` | `{ "image_url": "...", "duration": 5 }`      |
| **Audio Mix**       | POST    | `/v1/video/add/audio`     | `{ "video_url": "...", "audio_url": "..." }` |

## Tipp: Dynamische Parameter

Sie können n8n Expressions nutzen, um Daten von vorherigen Nodes zu übergeben:

```json
{
  "media_url": "{{ $json.url }}",
  "language": "en"
}
```

## Troubleshooting

- **Connection Refused**: Wenn n8n in Docker läuft, nutzen Sie `http://host.docker.internal:8080` statt `localhost`.
- **API Key Error**: Prüfen Sie den Header `x-api-key`.
- **Timeout**: Erhöhen Sie in n8n das Timeout für den HTTP Node, da manche Video-Operationen länger als 30s dauern können.
