# Scene Analyzer 🎬

Web-Applikation zur automatisierten Analyse von Drehbüchern und Treatments mit tabellarischer Szenen-Aufschlüsselung.

## 📋 Features (MVP v1.0)

- ✅ **Upload**: Fountain-Drehbücher (.fountain) und Plain Text hochladen
- ✅ **Parsing**: Automatische Szenen-Erkennung (INT/EXT, Location, Zeit)
- ✅ **Analyse**: Extraktion von Metadaten (Charaktere, Seitenzahl, geschätzte Länge)
- ✅ **Export**: CSV-Download der Analyse-Tabelle
- ✅ **UI**: Interaktive Tabelle (sortierbar, filterbar)

## 🏗️ Tech-Stack

### Backend
- **Python 3.12+** mit **FastAPI**
- **Pydantic** für Type-Safety
- **PostgreSQL** (optional für MVP)
- **Fountain** Parser

### Frontend
- **Astro 5** + **React** (Islands Architecture)
- **Tailwind CSS** für Styling
- **TanStack Table** für Tabellen
- **TypeScript** für Type-Safety

### Infrastructure
- **Docker** + **Docker Compose**
- **PostgreSQL** + **Redis**
- **Makefile** für Tasks

## 🚀 Quick Start

### Voraussetzungen
- **Docker** & **Docker Compose** installiert
- **Make** (für Makefile-Targets)
- Oder lokal: **Python 3.12+**, **Node.js 20+**, **Poetry**

### 1. Projekt klonen
```bash
git clone <repo-url> scene-analyzer
cd scene-analyzer
```

### 2. Mit Docker starten (empfohlen)
```bash
make docker-up
```

Services sind erreichbar unter:
- **Frontend**: http://localhost:4321
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

### 3. Logs anschauen
```bash
make docker-logs
```

### 4. Stoppen
```bash
make docker-down
```

---

## 🛠️ Lokale Entwicklung (ohne Docker)

### Backend Setup
```bash
cd backend

# Mit Poetry
poetry install
poetry run uvicorn app.main:app --reload

# Oder mit pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend läuft auf: http://localhost:8000

### Frontend Setup
```bash
cd frontend

npm install
npm run dev
```

Frontend läuft auf: http://localhost:4321

---

## 🧪 Testing

### Alle Tests ausführen
```bash
make test
```

### Tests mit Reporting (llm-rule v4.1 konform)
```bash
make test-report
```

Artefakte werden gespeichert in: `89_output/test_reports/<YYYYMMDD-HHMM>/`

### Backend-Tests einzeln
```bash
cd backend
poetry run pytest
poetry run pytest --cov=app  # Mit Coverage
```

### Frontend-Tests einzeln
```bash
cd frontend
npm test
npm run test:coverage  # Mit Coverage
```

---

## 📁 Projekt-Struktur

```
scene-analyzer/
├── 00_infos/              # Dokumentation
│   ├── llm-context.md     # Projekt-Kontext
│   ├── architecture.md    # System-Architektur
│   ├── grand-plan.md      # Entwicklungs-Roadmap
│   └── patterns.md        # Code-Patterns
├── 88_input/
│   └── testdata/          # Sample-Drehbücher
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
├── docker/                # Dockerfiles
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 📚 Dokumentation

Vollständige Dokumentation in `00_infos/`:
- **[llm-context.md](00_infos/llm-context.md)**: Projekt-Übersicht, Stack, Features
- **[architecture.md](00_infos/architecture.md)**: API-Design, Datenmodelle, Services
- **[grand-plan.md](00_infos/grand-plan.md)**: Entwicklungs-Phasen (MVP → v2.0 → v3.0)
- **[patterns.md](00_infos/patterns.md)**: Code-Patterns für Parser, Analyzer, API

---

## 🎯 Roadmap

### ✅ MVP (v1.0) - In Entwicklung
- Fountain-Format Support
- Basis-Analyse-Parameter
- CSV-Export
- Single-Session (keine Persistierung)

### 📅 Phase 2 (v2.0)
- PDF + Final Draft (.fdx) Support
- Erweiterte Analyse (Dialog-Anteil, Ton)
- Excel-Export + JSON
- Visualisierungen (Timeline, Charts)
- Persistierung (PostgreSQL)

### 📅 Phase 3 (v3.0)
- Multi-User (Auth via OAuth)
- Word (.docx) Support
- ML-Features (Sentiment-Analyse, Charakter-Arc)
- Public API mit API-Keys
- DSGVO-Compliance

---

## 🤝 Mitarbeit

Dieses Projekt folgt **llm-rule v4.1** für Entwicklung und Testing:
- Jede Änderung braucht Tests (Unit + Smoke)
- Test-Reports in `89_output/test_reports/`
- Coverage-Ziel: ~60% auf geändertem Code
- Git-Commits: `<type>(<scope>): <msg>; tests:<added|updated>; bump <file>@<old>-><new>`

---

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

## 👤 Autor

**johanneshoss**

---

**Version**: 1.0.0  
**Status**: In Entwicklung (MVP)  
**Letztes Update**: 14.10.2025
