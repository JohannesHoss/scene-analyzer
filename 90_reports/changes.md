---
title: Changes Log - Scene Analyzer
date: 14.10.2025
version: 1.0.0
status: initial
---

# Changes Log

## [1.0.0] - 14.10.2025 - Initial Setup

### Added
- ✅ Projekt-Struktur nach llm-rule v4.1 angelegt
- ✅ Dokumentation erstellt:
  - `00_infos/llm-context.md` - Projekt-Kontext
  - `00_infos/architecture.md` - System-Architektur
  - `00_infos/grand-plan.md` - Entwicklungs-Roadmap
  - `00_infos/patterns.md` - Code-Patterns
- ✅ Backend Setup (FastAPI):
  - `backend/pyproject.toml` - Dependencies
  - `backend/app/main.py` - FastAPI App mit Health-Endpoint
- ✅ Frontend Setup (Astro):
  - `frontend/package.json` - Dependencies
  - `frontend/astro.config.mjs` - Astro Config
  - `frontend/tailwind.config.mjs` - Tailwind Config
- ✅ Docker Setup:
  - `docker-compose.yml` - Multi-Service Orchestrierung
  - `docker/Dockerfile.backend` - Backend Container
  - `docker/Dockerfile.frontend` - Frontend Container
- ✅ Testing & Build:
  - `Makefile` mit `test-report` Target (llm-rule konform)
  - `.gitignore` für Python, Node, Docker
- ✅ Sample-Daten:
  - `88_input/testdata/sample.fountain` - Beispiel-Drehbuch
- ✅ README.md mit Quick Start Guide

### Changed
- Keine Änderungen (Initial Setup)

### Tests
- **Status**: ⏳ Keine Tests vorhanden
- **Coverage**: 0%
- **Geplant**: Parser-Tests, API-Tests, Frontend-Tests

### Betroffene Dateien
- Alle Projekt-Dateien (Initial Commit)

### Risiken & HOLDs
- **Keine HOLDs**
- **Risiken**: Keine (reiner Setup)

### Deployment
- **Status**: Lokal testbar mit `make docker-up`
- **Prod-Deployment**: Noch nicht durchgeführt

---

## Nächste Änderungen (geplant)

### M2: Backend Foundation (nächster Milestone)
- [ ] Fountain-Parser implementieren
- [ ] Upload-Endpoint (`POST /api/v1/scripts/upload`)
- [ ] Pydantic Models (Scene, Script)
- [ ] Unit-Tests für Parser
- [ ] Integration-Test: Upload → Parse

**Geplante Coverage**: ~70% für Parser-Modul

---

**Format für zukünftige Einträge**:

```markdown
## [X.Y.Z] - DD.MM.YYYY - Titel

### Added / Changed / Fixed / Removed
- Beschreibung der Änderung

### Tests
- **Added/Updated**: Welche Tests?
- **Coverage**: X% (Delta: +Y%)

### Betroffene Dateien
- `path/to/file1.py`
- `path/to/file2.ts`

### Risiken & HOLDs
- Evtl. Blocker oder offene Punkte

### Deployment
- Status, Hinweise
```

---

**Nächstes Update**: Nach M2 (Backend Foundation)
