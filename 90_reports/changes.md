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

---

## [1.1.0] - 14.10.2025 - M2: Backend Foundation Complete

### Added
- ✅ Pydantic Models:
  - `app/models/scene.py` - Scene domain model
  - `app/models/api.py` - API request/response models
- ✅ Parser System:
  - `app/parsers/base.py` - BaseParser interface
  - `app/parsers/exceptions.py` - Custom exceptions
  - `app/parsers/fountain_parser.py` - Fountain format parser
  - `app/parsers/registry.py` - Parser factory
- ✅ Service Layer:
  - `app/services/script_service.py` - Script upload & parsing logic
- ✅ API Endpoints:
  - `POST /api/v1/scripts/upload` - Upload & parse screenplay
  - `GET /api/v1/health` - Health check
- ✅ Tests (23 total):
  - Unit tests für FountainParser (12 tests)
  - Character extraction tests (4 tests)
  - API integration tests (7 tests)
  - All tests passing! 🎉

### Changed
- Updated `app/main.py` to register scripts router
- Fixed Python 3.9 compatibility (Optional type hints)
- Fixed INT/EXT normalization in parser
- Fixed character extraction with parentheticals

### Tests
- **Added**: 23 tests (100% passing)
- **Coverage**: 94% (exceeds 60% target by 34%!)
- **Modules**:
  - Parsers: 97%
  - Models: 100%
  - Services: 95%
  - API: 82%

### Betroffene Dateien
- `backend/app/models/*.py` (neu)
- `backend/app/parsers/*.py` (neu)
- `backend/app/services/*.py` (neu)
- `backend/app/api/scripts.py` (neu)
- `backend/app/main.py` (updated)
- `backend/tests/*.py` (neu)
- `backend/requirements.txt` (neu)

### Risiken & HOLDs
- **Keine HOLDs**
- **Risiko**: Fountain library version 0.1.3 (nicht 0.2.0) - minor issue
- **Risiko**: Python 3.9 compatibility required type hint changes

### Deployment
- **Status**: Backend API funktional und testbar
- **Testing**: `python3 -m pytest backend/tests/` - all passing
- **Next**: Frontend-Entwicklung (M4)

---

## Nächste Änderungen (geplant)

### M3: Analyzer-Logic (optional - kann übersprungen werden)
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
