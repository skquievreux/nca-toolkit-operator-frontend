---
title: "Dokumentations-Konzept (Governance v3.0)"
type: "architecture"
status: "approved"
last_updated: "2026-02-07"
---

# Dokumentations-Konzept

Dieses Dokument definiert die Standards und die Struktur der Projektdokumentation für das **NCA Toolkit** gemäß dem *AI Agent Governance Framework v3.0*.

## 1. Zweck
Die Dokumentation dient als zentrale Wissensbasis für Entwickler, Administratoren und KI-Agenten. Sie ist kristallklar, strukturiert und wartbar.

## 2. Struktur (5-Ebenen-Modell)

| Ebene  | Verzeichnis               | Inhalt                                             |
| :----- | :------------------------ | :------------------------------------------------- |
| **01** | `docs/01-architecture/`   | Konzepte, Architektur-Pläne, ADRs.                 |
| **02** | `docs/02-implementation/` | Setup-Guides, Integrations-Anleitungen (MCP, n8n). |
| **03** | `docs/03-operations/`     | Monitoring, Troubleshooting, Wartungsskripte.      |
| **04** | `docs/04-business/`       | Status-Reports, Roadmaps, Business Cases.          |
| **05** | `docs/05-reference/`      | API-Spezifikationen, Funktionslisten.              |

## 3. Formatierungsstandards

### Dateinamen
* Alle Dateinamen müssen in **kebab-case** verfasst sein (z.B. `mcp-integration.md`).
* Keine Sonderzeichen oder Leerzeichen.

### YAML Frontmatter
Jede Datei startet verpflichtend mit:
```yaml
---
title: "Präziser Dokumententitel"
type: "architecture | implementation | operations | business | reference"
status: "draft | review | approved | deprecated"
last_updated: "YYYY-MM-DD"
---
```

### Schreibstil
* **Präzision:** Fakten vor Füllwörter.
* **Aktiv:** "Der Server führt aus..." statt "Es wird ausgeführt...".
* **Klarheit:** Keine Jargon-Begriffe ohne kurze Definition bei Ersteinführung.

## 4. Änderungsverfügung
Änderungen an der Dokumentationsstruktur bedürfen einer Überprüfung der internen Verlinkungen, um die Konsistenz zu gewährleisten.
