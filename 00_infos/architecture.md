---
title: Scene Analyzer - Architecture
version: 1.0
date: 14.10.2025
owner: johanneshoss
status: active
depends_on:
  - llm-context.md@1.0
summary: System-Architektur, API-Design, Datenmodelle und Service-Layer für Scene Analyzer.
---

# Scene Analyzer - Architecture v1.0

## 🏛️ System-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      TRAEFIK (Proxy)                         │
│  - SSL Termination                                           │
│  - Routing: /api/* → Backend, /* → Frontend                 │
└─────┬──────────────────────────────────────────┬────────────┘
      │                                           │
      │ /api/*                                    │ /*
      ▼                                           ▼
┌────────────────────┐                  ┌──────────────────────┐
│  FASTAPI BACKEND   │                  │   ASTRO FRONTEND     │
│  (Python 3.12+)    │                  │   (Node.js 20+)      │
│                    │                  │                      │
│  - REST API        │                  │  - Static Site       │
│  - File Upload     │◄─────────────────┤  - Islands UI        │
│  - Parser Engine   │   Fetch API      │  - TanStack Table    │
│  - Analyzer Logic  │                  │  - Chart.js          │
└────────┬───────────┘                  └──────────────────────┘
         │
         │ Read/Write
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      POSTGRESQL 16                           │
│  - Scripts (metadata, optional)                              │
│  - Analyses (results)                                        │
│  - Users (Phase 3)                                           │
└──────────────────────────────────────────────────────────────┘
         │
         │ Optional
         ▼
┌─────────────────────────────────────────────────────────────┐
│                         REDIS 7                              │
│  - Job Queue (Celery, für große Files)                      │
│  - Session Cache                                             │
└──────────────────────────────────────────────────────────────┘
         │
         │ Optional
         ▼
┌─────────────────────────────────────────────────────────────┐
│                      MINIO / S3                              │
│  - Uploaded Scripts (encrypted)                              │
│  - Generated Reports (CSV, Excel)                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 API-Design (REST)

### Basis-URL
- **Dev**: `http://localhost:8000/api/v1`
- **Prod**: `https://scene-analyzer.yourdomain.com/api/v1`

### Endpoints (MVP)

#### 1. Upload & Parse Script
```http
POST /api/v1/scripts/upload
Content-Type: multipart/form-data

Body:
  file: <binary>
  format: "fountain" | "plaintext" | "pdf" | "fdx" | "docx"

Response 201:
{
  "script_id": "uuid-1234",
  "filename": "my-script.fountain",
  "format": "fountain",
  "scenes_count": 42,
  "pages": 90,
  "upload_time": "2025-10-14T16:18:25Z"
}
```

#### 2. Analyze Script
```http
POST /api/v1/scripts/{script_id}/analyze
Content-Type: application/json

Body:
{
  "parameters": [
    "scene_number",
    "int_ext",
    "location",
    "time",
    "characters",
    "page_number",
    "estimated_length"
  ]
}

Response 200:
{
  "analysis_id": "uuid-5678",
  "script_id": "uuid-1234",
  "scenes": [
    {
      "scene_number": 1,
      "int_ext": "INT",
      "location": "WOHNUNG BERLIN",
      "time": "TAG",
      "characters": ["ANNA", "PETER"],
      "page_number": 1,
      "estimated_length": 2.5
    },
    ...
  ],
  "total_scenes": 42,
  "total_pages": 90,
  "total_runtime_estimate": 90
}
```

#### 3. Export Analysis
```http
GET /api/v1/analyses/{analysis_id}/export?format=csv

Response 200:
Content-Type: text/csv
Content-Disposition: attachment; filename="analysis-uuid-5678.csv"

Szene,INT/EXT,Location,Zeit,Charaktere,Seite,Länge
1,INT,WOHNUNG BERLIN,TAG,"ANNA, PETER",1,2.5
...
```

#### 4. Get Script Details
```http
GET /api/v1/scripts/{script_id}

Response 200:
{
  "script_id": "uuid-1234",
  "filename": "my-script.fountain",
  "format": "fountain",
  "scenes_count": 42,
  "pages": 90,
  "upload_time": "2025-10-14T16:18:25Z",
  "analyses": [
    {
      "analysis_id": "uuid-5678",
      "created_at": "2025-10-14T16:20:00Z"
    }
  ]
}
```

#### 5. Health Check
```http
GET /api/v1/health

Response 200:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

---

## 📦 Datenmodelle (Pydantic)

### ScriptUpload (Input)
```python
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ScriptFormat(str, Enum):
    FOUNTAIN = "fountain"
    PLAINTEXT = "plaintext"
    PDF = "pdf"
    FDX = "fdx"
    DOCX = "docx"

class ScriptUploadResponse(BaseModel):
    script_id: str
    filename: str
    format: ScriptFormat
    scenes_count: int
    pages: int
    upload_time: datetime
```

### Scene (Core Model)
```python
class Scene(BaseModel):
    scene_number: int
    int_ext: str | None  # "INT", "EXT", "INT/EXT"
    location: str | None
    time: str | None  # "TAG", "NACHT", etc.
    characters: list[str]
    page_number: int
    estimated_length: float  # in minutes
    action_lines: int | None  # Phase 2
    dialog_lines: int | None  # Phase 2
    tone: str | None  # Phase 2
```

### AnalysisRequest (Input)
```python
class AnalysisRequest(BaseModel):
    parameters: list[str]  # Parameter-Namen
```

### AnalysisResponse (Output)
```python
class AnalysisResponse(BaseModel):
    analysis_id: str
    script_id: str
    scenes: list[Scene]
    total_scenes: int
    total_pages: int
    total_runtime_estimate: int
    created_at: datetime
```

---

## 🧩 Backend-Architektur (Layered)

### 1. API Layer (`backend/app/api/`)
- **Routes**: FastAPI Router
- **Validation**: Pydantic Models
- **Error Handling**: HTTP Exceptions

```python
# backend/app/api/scripts.py
from fastapi import APIRouter, UploadFile, HTTPException
from app.services.parser_service import ParserService
from app.services.analyzer_service import AnalyzerService

router = APIRouter(prefix="/scripts", tags=["scripts"])

@router.post("/upload")
async def upload_script(file: UploadFile):
    parser = ParserService()
    result = await parser.parse_script(file)
    return result
```

### 2. Service Layer (`backend/app/services/`)
- **Business Logic**: Parser, Analyzer
- **Orchestration**: Kombiniert Parser + Analyzer

```python
# backend/app/services/parser_service.py
class ParserService:
    def __init__(self):
        self.parsers = {
            "fountain": FountainParser(),
            "plaintext": PlainTextParser(),
            # ...
        }
    
    async def parse_script(self, file: UploadFile):
        format = self._detect_format(file)
        parser = self.parsers[format]
        scenes = parser.parse(file.file.read())
        return {"scenes": scenes, "format": format}
```

### 3. Parser Layer (`backend/app/parsers/`)
- **Format-spezifisch**: Ein Parser pro Format
- **Interface**: Gemeinsame `BaseParser` Klasse

```python
# backend/app/parsers/base.py
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: bytes) -> list[Scene]:
        pass

# backend/app/parsers/fountain_parser.py
class FountainParser(BaseParser):
    def parse(self, content: bytes) -> list[Scene]:
        # Fountain-Parsing-Logik
        pass
```

### 4. Analyzer Layer (`backend/app/analyzers/`)
- **Szenen-Analyse**: Metadaten extrahieren
- **Charakter-Erkennung**: Aus Dialogen
- **Heuristik**: INT/EXT, Zeit, Location

```python
# backend/app/analyzers/scene_analyzer.py
class SceneAnalyzer:
    def analyze(self, scenes: list[Scene], parameters: list[str]) -> list[Scene]:
        for scene in scenes:
            if "characters" in parameters:
                scene.characters = self._extract_characters(scene)
            if "estimated_length" in parameters:
                scene.estimated_length = self._estimate_length(scene)
        return scenes
```

### 5. Database Layer (`backend/app/db/`)
- **SQLAlchemy**: ORM
- **Migrations**: Alembic

```python
# backend/app/db/models.py
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(UUID, primary_key=True)
    filename = Column(String, nullable=False)
    format = Column(String, nullable=False)
    scenes_count = Column(Integer)
    pages = Column(Integer)
    upload_time = Column(DateTime)
```

---

## 🎨 Frontend-Architektur (Astro Islands)

### Struktur
```
frontend/src/
├── pages/
│   ├── index.astro         # Landing Page
│   ├── upload.astro        # Upload-Formular
│   └── analysis/
│       └── [id].astro      # Analyse-Ansicht
├── components/
│   ├── UploadForm.tsx      # File Upload (React Island)
│   ├── SceneTable.tsx      # TanStack Table (React Island)
│   ├── ExportButton.tsx    # Export-Optionen
│   └── Header.astro        # Static Header
├── layouts/
│   └── Layout.astro        # Basis-Layout
└── lib/
    ├── api.ts              # API-Client (fetch wrapper)
    └── types.ts            # TypeScript Typen
```

### API-Client
```typescript
// frontend/src/lib/api.ts
const API_BASE = import.meta.env.PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function uploadScript(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${API_BASE}/scripts/upload`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) throw new Error("Upload failed");
  return response.json();
}

export async function analyzeScript(scriptId: string, parameters: string[]) {
  const response = await fetch(`${API_BASE}/scripts/${scriptId}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ parameters }),
  });
  
  if (!response.ok) throw new Error("Analysis failed");
  return response.json();
}
```

---

## 🐳 Docker-Setup

### Services (docker-compose.yml)
```yaml
services:
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./docker/traefik.yml:/traefik.yml

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/scene_analyzer
      REDIS_URL: redis://redis:6379/0
    labels:
      - "traefik.http.routers.backend.rule=PathPrefix(`/api`)"

  frontend:
    build: ./frontend
    labels:
      - "traefik.http.routers.frontend.rule=PathPrefix(`/`)"

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: scene_analyzer
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

---

## 🔐 Security

### MVP
- **Input Validation**: Pydantic + File-Type-Check
- **File Size Limit**: Max 50 MB
- **Rate Limiting**: FastAPI Middleware (10 req/min)
- **CORS**: Configured für Frontend-Domain

### Phase 2
- **Auth**: JWT Tokens
- **File Encryption**: S3/MinIO Server-Side Encryption
- **HTTPS**: Traefik + Let's Encrypt

---

## 📈 Skalierung (Future)

### Horizontal Scaling
- **Backend**: Mehrere FastAPI-Instanzen hinter Traefik
- **Database**: PostgreSQL Read Replicas
- **Redis**: Redis Cluster

### Async Processing
- **Celery**: Für große PDF-Verarbeitung
- **Queue**: Redis als Broker
- **Workers**: Separate Container

---

## 🧪 Testing-Strategie

### Backend
- **Unit**: Parser, Analyzer-Logik (`tests/unit/`)
- **Integration**: API-Endpoints (`tests/integration/`)
- **Fixtures**: Sample-Drehbücher (`tests/fixtures/`)

### Frontend
- **Unit**: API-Client, Utils (`tests/unit/`)
- **Component**: React Components (Vitest)
- **E2E**: Upload → Analyze → Export (Playwright)

---

**Version**: 1.0  
**Letztes Update**: 14.10.2025  
**Nächstes Review**: Nach Backend-MVP
