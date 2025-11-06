# Scene Analyzer

## 📁 Projekt-Struktur

```
scene-analyzer/
├── backend/               # Python/FastAPI
│   ├── app/
│   │   ├── api/           # REST Endpoints
│   │   ├── parsers/       # Drehbuch-Parser
│   │   ├── analyzers/     # Szenen-Analyse
│   │   ├── models/        # Pydantic Models
│   │   └── services/      # Business Logic
│   ├── tests/
│   └── pyproject.toml
├── frontend/              # Astro + React + Tailwind
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

## 🏗️ Tech-Stack

### Backend
- **Python 3.12+** mit **FastAPI**
- **Pydantic** für Type-Safety
- **PostgreSQL** (optional für MVP)
- **Redis** (für Job Queue, optional)
- Parser: fountain-py, pypdf2, lxml (FDX)

### Frontend
- **Astro 5** + **React Islands Architecture**
- **Tailwind CSS** für Styling
- **TanStack Table** für Tabellen
- **TypeScript** für Type-Safety

### Infrastructure
- **Docker** + **Docker Compose**
- **PostgreSQL 16**
- **Redis 7** (optional)
- **Traefik** (Reverse Proxy)

### Development & Testing
- **Pytest** (Backend)
- **Vitest** (Frontend)
- **Playwright** (E2E Tests)
- **Coverage-Reporting**
- **Makefile** für Task-Automatisierung

---

**Bereit für die Planung.**
