# Architektur-Konzept: ZOT (Zentraler Orientierungs-Teil)

## 🎯 Zielsetzung
Dynamische Erkennung und Nutzung von API-Endpunkten des MCP-Servers zur Laufzeit. Anstatt Endpunkte hart im Code zu verdrahten, fragen wir den Server "Was kannst du?" und instruieren das LLM entsprechend.

## 🏗️ Komponenten

### 1. Discovery Service (`server/discovery_service.py`)
- **Aufgabe**: Startet beim Booten (und periodisch) eine Anfrage an den MCP-Server (z.B. `/v1/tools/list` oder `/v1/capabilities`).
- **Fallback**: Nutzt lokale Definitionen, falls der Server nicht antwortet.
- **Cache**: Speichert die Ergebnisse im Speicher/DB, um Latenz zu vermeiden.

### 2. Dynamic Prompt Builder (`server/prompt_builder.py`)
- **Input**: Liste der verfügbaren Tools aus dem Discovery Service.
- **Output**: Generiert den `SYSTEM_PROMPT` für `llm_service.py` neu.
- **Vorteil**: Wenn neue Features (z.B. `/v1/video/super-slowmo`) deployed werden, erkennt der Agent sie sofort ohne Code-Änderung.

### 3. ZOT-Registry (Frontend & Backend)
- Ein zentraler Endpunkt `/api/zot/capabilities`, der dem Frontend mitteilt, welche Features aktiv sind (z.B. "Zeige RSS-Button nur, wenn RSS-Dienst verfügbar").

## 🚀 Implementierungs-Schritte

1. **Analyse**: Prüfen, was `endpoint_discovery.py` bereits leistet.
2. **Refactoring**: `llm_service.py` so umbauen, dass es den Prompt *wirklich* dynamisch bei jedem Request baut (bzw. cached), statt hardcoded Strings zu nutzen.
3. **Integration**: RSS-Dienste als "lokale Capability" in den Discovery-Prozess einpflegen.

## ✅ Vorteile
- **Wartbarkeit**: Kein manuelles Nachpflegen von System-Prompts.
- **Robustheit**: Agent halluziniert keine nicht-existenten Endpunkte.
- **Skalierbarkeit**: Neue MCP-Tools sind sofort nutzbar.
