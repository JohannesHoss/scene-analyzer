# Scene Analyzer - Drehbuch-Analyse Tool

Vollautomatisches Analyse-Tool für Drehbücher und Treatments mit AI-Integration.

## 📚 Dokumentation

- **[IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md)** - Detaillierter Schritt-für-Schritt Implementierungsplan
- **[CLAUDE.md](CLAUDE.md)** - System-Referenz für AI-Agents
- **[scene-analyzer.md](scene-analyzer.md)** - Vollständige Projekt-Spezifikation

## 🚀 Entwicklungs-Phasen

### Status-Übersicht

| Phase | Status | Branch | Tag | Beschreibung |
|-------|--------|--------|-----|--------------|
| **Phase 1** | ⏳ Geplant | `phase-1-docker-setup` | `v0.1.0` | Docker & Basis-Setup |
| **Phase 2** | ⏳ Geplant | `phase-2-backend-core` | `v0.2.0` | Backend Core API |
| **Phase 3** | ⏳ Geplant | `phase-3-ai-integration` | `v0.3.0` | AI Integration |
| **Phase 4** | ⏳ Geplant | `phase-4-excel-generation` | `v0.4.0` | Excel Generation |
| **Phase 5** | ⏳ Geplant | `phase-5-frontend` | `v0.5.0` | Frontend UI |
| **Phase 6** | ⏳ Geplant | `phase-6-integration` | `v1.0.0` | Integration & Testing |

### Workflow

```bash
# Neue Phase starten
git checkout main
git pull
git checkout -b phase-X-name

# Entwickeln & committen
git add .
git commit -m "feat(scope): Description"

# Zu GitHub pushen
git push -u origin phase-X-name

# Nach Merge: Tag erstellen
git checkout main
git pull
git tag -a v0.X.0 -m "Phase X completed"
git push --tags
```

## 🏗️ Technologie-Stack

### Backend
- Python 3.12+ mit FastAPI
- OpenRouter API für AI-Analyse
- PDF/DOCX/TXT Parsing
- Excel-Generation mit openpyxl

### Frontend
- Nginx Static Server
- Vanilla JavaScript
- Tailwind CSS (CDN)

### Infrastructure
- Docker Compose
- 2 Container Setup (Backend Port 8001, Frontend Port 3000)
- Stateless Architecture (No Database)

## 🎯 Features

- ✅ PDF, DOCX, TXT Upload
- ✅ Multi-Language Support (DE/EN)
- ✅ 4 Analyse-Modi (Standard, Tatort, Story, Combined)
- ✅ Automatische Szenen-Erkennung
- ✅ AI-powered Analyse via OpenRouter
- ✅ Excel-Export mit formatierter Ausgabe
- ✅ Progress-Tracking in Echtzeit
- ✅ Kosten-Transparenz

## 📦 Quick Start (Nach MVP-Fertigstellung)

```bash
# 1. Repository klonen
git clone https://github.com/JohannesHoss/scene-analyzer.git
cd scene-analyzer

# 2. Environment Setup
echo "OPENROUTER_API_KEY=your-key-here" > .env

# 3. Docker starten
docker-compose up

# 4. Browser öffnen
open http://localhost:3000
```

## 📝 Git Commit Convention

```
<type>(<scope>): <subject>
```

**Types:**
- `feat`: Neue Funktion
- `fix`: Bugfix
- `docs`: Dokumentation
- `style`: Formatierung
- `refactor`: Code-Umstrukturierung
- `test`: Tests
- `chore`: Wartungsarbeiten

**Beispiele:**
```bash
git commit -m "feat(parser): Add PDF scene extraction"
git commit -m "fix(api): Handle upload errors correctly"
git commit -m "docs: Update README with phase status"
```

## 🧪 Testing

Manuelle Tests mit Beispiel-Drehbüchern in `examples/`:
- `examples/screenplays/` - Drehbuch-Beispiele
- `examples/treatments/` - Treatment-Beispiele

## 📄 Lizenz

Privates Projekt - Alle Rechte vorbehalten

---

**Entwickelt von:** Johannes Hoss  
**Status:** In Entwicklung (Phase 1 vorbereitet)  
**Letzte Aktualisierung:** November 2024