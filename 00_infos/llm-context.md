---
title: Scene Analyzer - LLM Context
version: 1.0
date: 14.10.2025
owner: johanneshoss
status: active
depends_on:
  - architecture.md@1.0
  - grand-plan.md@1.0
summary: Web-Applikation zur Analyse von Drehbüchern und Treatments mit tabellarischer Szenen-Aufschlüsselung.
---

# Scene Analyzer - LLM Context v1.0

## 🎬 Projekt-Überblick

**Scene Analyzer** ist ein Web-Tool zur automatisierten Analyse von Drehbüchern und Treatments. Es extrahiert Szenen-Informationen und generiert strukturierte Tabellen mit konfigurierbaren Analyse-Parametern.

### Kernfunktionalität
- **Upload**: Drehbücher hochladen (Fountain, Plain Text; später PDF, FDX, DOCX)
- **Parsing**: Automatische Erkennung von Szenen-Struktur
- **Analyse**: Extraktion von Metadaten pro Szene
- **Export**: Tabellarische Ausgabe (CSV, Excel, JSON)

### Zielgruppe
- Drehbuchautoren
- Produktionsplanung
- Script Supervisors
- Regisseure & Producer

---

## 🏗️ Technologie-Stack

### Frontend
- **Astro 5.x**: Static Site Generation + Islands Architecture
- **Tailwind CSS**: Utility-first Styling
- **TanStack Table**: Sortierbare, filterbare Tabellen
- **Chart.js**: Visualisierungen (Timeline, Statistiken)
- **Dropzone**: File Upload (Drag & Drop)

### Backend
- **Python 3.12+**: Core Language
- **FastAPI**: REST API Framework
- **Pydantic**: Type-safe Models
- **PostgreSQL**: Persistierung von Analysen
- **Redis**: Job Queue & Caching (optional für async processing)

### Parsing-Libraries
- **fountain**: Fountain-Format (.fountain)
- **pypdf2**: PDF-Extraktion
- **python-docx**: Word-Dokumente
- **beautifulsoup4**: HTML/XML-Parsing (Final Draft FDX)
- **spacy** (optional): NLP für Charakter-Erkennung

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Orchestrierung (dev + prod)
- **Traefik**: Reverse Proxy + SSL
- **MinIO / S3**: File Storage (hochgeladene Drehbücher)

### Testing & CI
- **Backend**: Pytest + pytest-cov
- **Frontend**: Vitest (Astro/Vite)
- **E2E**: Playwright
- **Reports**: llm-rule v4.1 konform (`89_output/test_reports/`, `90_reports/`)

---

## 📊 Analyse-Parameter (pro Szene)

### MVP (Phase 1)
1. **Szenen-Nummer**: Automatisch oder aus Header
2. **INT/EXT**: Innen/Außen
3. **Location**: Schauplatz (z.B. "WOHNUNG BERLIN")
4. **Zeit**: TAG / NACHT / DÄMMERUNG
5. **Seitenzahl**: Start-Seite
6. **Geschätzte Länge**: Minuten (1 Seite ≈ 1 Minute)
7. **Charaktere**: Handelnde Figuren (aus Dialog-Headers)

### Phase 2
8. **Dialog-Anteil**: % Dialog vs. Action
9. **Action-Beschreibung**: Anzahl Zeilen Action
10. **Emotionaler Ton**: Heuristik/ML (Spannung, Komödie, Drama)
11. **Requisiten**: Erkannte Props (z.B. "Waffe", "Telefon")
12. **SFX/VFX**: Special Effects Marker

### Phase 3 (Optional)
13. **Charakter-Entwicklung**: Arc-Tracking über Szenen
14. **Kosten-Schätzung**: Budget-Kategorie (A/B/C)
15. **Produktions-Komplexität**: Schwierigkeitsgrad (1-10)

---

## 🔄 Workflow (User Journey)

```
1. User landet auf Startseite
   ↓
2. Upload Drehbuch (Drag & Drop oder File Picker)
   ↓
3. Format-Erkennung (Fountain, PDF, etc.)
   ↓
4. Parsing & Szenen-Extraktion
   ↓
5. Analyse-Parameter auswählen (Checkboxen)
   ↓
6. Tabelle wird generiert
   ↓
7. Interaktive Ansicht (sortieren, filtern)
   ↓
8. Export (CSV, Excel, JSON)
   ↓
9. Optional: Speichern für spätere Bearbeitung
```

---

## 🎯 Projekt-Phasen

### MVP (Version 1.0)
- **Fountain-Support**: `.fountain` Dateien parsen
- **Plain Text Heuristik**: INT./EXT. erkennen
- **Basis-Parameter**: Szene, INT/EXT, Location, Zeit, Charaktere, Seiten
- **CSV-Export**: Einfache Tabelle
- **Single-User**: Keine Accounts

### Phase 2 (Version 2.0)
- **PDF-Support**: Text-Extraktion
- **Final Draft FDX**: XML-Parsing
- **Erweiterte Analyse**: Dialog-Anteil, Ton, Action
- **Excel-Export**: Formatierte Tabellen
- **Visualisierungen**: Timeline, Charakter-Frequenz

### Phase 3 (Finalisierung)
- **Multi-User**: Accounts, Speichern von Projekten
- **Word-Support**: DOCX-Parsing
- **ML-Features**: Sentiment-Analyse, Charakter-Arc
- **API**: Public API für Integrationen

---

## 🗂️ Drehbuch-Formate (Priorität)

### Fountain (.fountain) - MVP
- **Plain Text Format**: Einfach zu parsen
- **Standard**: Open-Source Screenwriting Format
- **Struktur**:
  ```
  INT. WOHNUNG BERLIN - TAG

  Action-Beschreibung hier.

  CHARAKTER
  Dialog hier.
  ```

### Plain Text - MVP
- **Heuristik**: `INT.` / `EXT.` erkennen
- **Regex-basiert**: Szenen-Header extrahieren

### PDF - Phase 2
- **Herausforderung**: Layout-abhängig, keine Struktur
- **Ansatz**: pypdf2 + Heuristik

### Final Draft (.fdx) - Phase 2
- **XML-Format**: Gut strukturiert
- **Parsing**: BeautifulSoup + lxml

### Word (.docx) - Phase 3
- **python-docx**: Paragraph-basiert
- **Heuristik**: Ähnlich wie Plain Text

---

## 🔒 Datenschutz & Security

### MVP
- **Keine Persistierung**: Drehbücher werden nach Analyse gelöscht
- **Temporäre Files**: `/tmp/` oder Redis
- **Kein Login**: Single-Session

### Phase 2
- **Optional Save**: User kann Analyse speichern (mit Token)
- **Verschlüsselung**: S3/MinIO mit Encryption at Rest

### Phase 3
- **User Accounts**: Auth via OAuth (Google, GitHub)
- **DSGVO-konform**: Daten-Export, Löschung auf Anfrage

---

## 🚀 Deployment

### Development
- **Docker Compose**: Alle Services lokal
- **Hot Reload**: Frontend (Astro) + Backend (FastAPI)

### Production
- **VPS/Cloud**: DigitalOcean, Hetzner, AWS
- **Traefik**: Reverse Proxy + Let's Encrypt SSL
- **PostgreSQL**: Managed oder Container
- **Redis**: Optional für Queue

---

## 📁 Projekt-Struktur (llm-rule konform)

```
scene-analyzer/
├── 00_infos/              # Dokumentation
│   ├── llm-context.md     # Dieses Dokument
│   ├── architecture.md    # System-Design
│   ├── grand-plan.md      # Entwicklungs-Roadmap
│   └── patterns.md        # Code-Patterns
├── 88_input/
│   └── testdata/          # Sample-Drehbücher (anonymisiert)
├── 89_output/
│   └── test_reports/      # Test-Artefakte (timestamped)
├── 90_reports/            # Human-readable Reports
│   ├── test-report.md
│   ├── coverage.md
│   └── changes.md
├── backend/               # Python/FastAPI
│   ├── app/
│   │   ├── api/           # REST Endpoints
│   │   ├── parsers/       # Drehbuch-Parser
│   │   ├── analyzers/     # Szenen-Analyse
│   │   └── models/        # Pydantic Models
│   ├── tests/
│   └── pyproject.toml
├── frontend/              # Astro + Tailwind
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── layouts/
│   └── package.json
├── docker/                # Container-Configs
├── docker-compose.yml
├── Makefile               # test-report, dev, deploy
└── README.md
```

---

## ⚙️ Entwicklungs-Guidelines (llm-rule v4.1)

### Coding
- **Modular**: Dateien <300 Zeilen
- **Type-safe**: Pydantic (Backend), TypeScript (Frontend)
- **DRY**: Keine Duplikate
- **Lokalisierung**: Europe/Vienna, Datum 30.05.2025, Geld 10.320,00 €

### Testing (Pflicht)
- **Unit**: Jede Logik-Änderung
- **Smoke**: Happy Path
- **Coverage**: ~60% auf geändertem Code
- **Runner**: `make test-report` → `89_output/test_reports/<YYYYMMDD-HHMM>/`

### Reporting (Pflicht)
- **90_reports/test-report.md**: Suite-Ergebnisse
- **90_reports/coverage.md**: Coverage-Zahlen
- **90_reports/changes.md**: Änderungen, Tests, Risiken

### Git
- **Branch**: `feat/`, `fix/`, `docs/`, `chore/`
- **Commit**: `<type>(<scope>): <msg>; tests:<added|updated>; bump <file>@<old>-><new>`

---

## 🎯 HOLDs & Blocker

*Aktuell keine HOLDs.*

---

## 📚 Referenzen

- **Fountain Spec**: https://fountain.io/syntax
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Astro Docs**: https://astro.build
- **llm-rule v4.1**: Siehe Rules

---

**Version**: 1.0  
**Letztes Update**: 14.10.2025  
**Nächstes Review**: Nach MVP-Fertigstellung
