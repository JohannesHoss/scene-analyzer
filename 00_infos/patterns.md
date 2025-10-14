---
title: Scene Analyzer - Code Patterns
version: 1.0
date: 14.10.2025
owner: johanneshoss
status: active
depends_on:
  - llm-context.md@1.0
  - architecture.md@1.0
summary: Wiederverwendbare Code-Patterns für Parser, Analyzer und API-Endpoints.
---

# Scene Analyzer - Code Patterns v1.0

## 🎯 Übersicht

Dieses Dokument sammelt bewährte Code-Patterns für Scene Analyzer. Neue Patterns werden hier dokumentiert, bestehende Patterns werden bei Bedarf angepasst.

---

## 1. Parser Pattern (Strategy Pattern)

### Basis-Interface
```python
# backend/app/parsers/base.py
from abc import ABC, abstractmethod
from typing import List
from app.models.scene import Scene

class BaseParser(ABC):
    """Basis-Klasse für alle Format-Parser."""
    
    @abstractmethod
    def parse(self, content: bytes) -> List[Scene]:
        """
        Parst den Drehbuch-Content und gibt Liste von Szenen zurück.
        
        Args:
            content: Datei-Content als bytes
            
        Returns:
            Liste von Scene-Objekten
            
        Raises:
            ParsingError: Bei Parsing-Fehlern
        """
        pass
    
    @abstractmethod
    def can_parse(self, filename: str, content: bytes) -> bool:
        """
        Prüft, ob dieser Parser das Format verarbeiten kann.
        
        Args:
            filename: Dateiname
            content: Datei-Content (erste 1024 bytes für Detection)
            
        Returns:
            True wenn Parser zuständig ist
        """
        pass
```

### Konkreter Parser (Beispiel: Fountain)
```python
# backend/app/parsers/fountain_parser.py
import re
from typing import List
from app.parsers.base import BaseParser
from app.models.scene import Scene
from app.parsers.exceptions import ParsingError

class FountainParser(BaseParser):
    """Parser für Fountain-Format (.fountain)."""
    
    SCENE_HEADING_PATTERN = re.compile(
        r'^(INT|EXT|INT\./EXT|I/E)[\.\s]+(.+?)(?:\s+-\s+(.+))?$',
        re.IGNORECASE | re.MULTILINE
    )
    
    CHARACTER_PATTERN = re.compile(r'^[A-Z\s]+$', re.MULTILINE)
    
    def can_parse(self, filename: str, content: bytes) -> bool:
        return filename.endswith('.fountain') or \
               self.SCENE_HEADING_PATTERN.search(content.decode('utf-8', errors='ignore'))
    
    def parse(self, content: bytes) -> List[Scene]:
        try:
            text = content.decode('utf-8')
            scenes = self._extract_scenes(text)
            return scenes
        except Exception as e:
            raise ParsingError(f"Fountain parsing failed: {e}")
    
    def _extract_scenes(self, text: str) -> List[Scene]:
        scenes = []
        lines = text.split('\n')
        current_scene = None
        scene_number = 1
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Scene Heading erkennen
            match = self.SCENE_HEADING_PATTERN.match(line)
            if match:
                if current_scene:
                    scenes.append(current_scene)
                
                int_ext = match.group(1).upper()
                location = match.group(2).strip()
                time = match.group(3).strip() if match.group(3) else None
                
                current_scene = Scene(
                    scene_number=scene_number,
                    int_ext=int_ext,
                    location=location,
                    time=time,
                    page_number=self._estimate_page(i, len(lines))
                )
                scene_number += 1
        
        if current_scene:
            scenes.append(current_scene)
        
        return scenes
    
    def _estimate_page(self, line_number: int, total_lines: int) -> int:
        """Schätzt Seitenzahl basierend auf Zeilen (55 Zeilen ≈ 1 Seite)."""
        return max(1, line_number // 55)
```

### Parser-Registry (Factory Pattern)
```python
# backend/app/parsers/registry.py
from typing import List
from app.parsers.base import BaseParser
from app.parsers.fountain_parser import FountainParser
from app.parsers.plaintext_parser import PlainTextParser
from app.parsers.exceptions import UnsupportedFormatError

class ParserRegistry:
    """Registry für alle verfügbaren Parser."""
    
    def __init__(self):
        self.parsers: List[BaseParser] = [
            FountainParser(),
            PlainTextParser(),
            # Weitere Parser hier
        ]
    
    def get_parser(self, filename: str, content: bytes) -> BaseParser:
        """
        Findet passenden Parser basierend auf Dateiname und Content.
        
        Args:
            filename: Dateiname
            content: Erste bytes der Datei
            
        Returns:
            Passender Parser
            
        Raises:
            UnsupportedFormatError: Wenn kein Parser gefunden wurde
        """
        for parser in self.parsers:
            if parser.can_parse(filename, content[:1024]):
                return parser
        
        raise UnsupportedFormatError(f"No parser found for {filename}")
```

---

## 2. Analyzer Pattern (Pipeline Pattern)

### Basis-Analyzer
```python
# backend/app/analyzers/base.py
from abc import ABC, abstractmethod
from typing import List
from app.models.scene import Scene

class BaseAnalyzer(ABC):
    """Basis-Klasse für Szenen-Analysen."""
    
    @abstractmethod
    def analyze(self, scenes: List[Scene]) -> List[Scene]:
        """
        Führt Analyse auf Szenen durch und reichert sie an.
        
        Args:
            scenes: Liste von Szenen
            
        Returns:
            Angereicherte Szenen (in-place Modifikation möglich)
        """
        pass
    
    @property
    @abstractmethod
    def required_parameters(self) -> List[str]:
        """Liste der Parameter, die dieser Analyzer benötigt."""
        pass
```

### Konkreter Analyzer (Beispiel: Charaktere)
```python
# backend/app/analyzers/character_analyzer.py
import re
from typing import List, Set
from app.analyzers.base import BaseAnalyzer
from app.models.scene import Scene

class CharacterAnalyzer(BaseAnalyzer):
    """Extrahiert Charaktere aus Szenen."""
    
    CHARACTER_PATTERN = re.compile(
        r'^([A-Z][A-Z\s]{2,})$',
        re.MULTILINE
    )
    
    @property
    def required_parameters(self) -> List[str]:
        return ['characters']
    
    def analyze(self, scenes: List[Scene]) -> List[Scene]:
        for scene in scenes:
            if not scene.raw_content:
                continue
            
            characters = self._extract_characters(scene.raw_content)
            scene.characters = list(characters)
        
        return scenes
    
    def _extract_characters(self, content: str) -> Set[str]:
        """Extrahiert Charakternamen aus Content."""
        characters = set()
        
        for match in self.CHARACTER_PATTERN.finditer(content):
            name = match.group(1).strip()
            # Filter: Min 3 Zeichen, max 30 Zeichen, keine reinen Zahlen
            if 3 <= len(name) <= 30 and not name.isdigit():
                characters.add(name)
        
        return characters
```

### Analyzer-Pipeline
```python
# backend/app/analyzers/pipeline.py
from typing import List
from app.analyzers.base import BaseAnalyzer
from app.analyzers.character_analyzer import CharacterAnalyzer
from app.analyzers.length_analyzer import LengthAnalyzer
from app.models.scene import Scene

class AnalyzerPipeline:
    """Pipeline für sequentielle Szenen-Analyse."""
    
    ANALYZERS = {
        'characters': CharacterAnalyzer,
        'estimated_length': LengthAnalyzer,
        # Weitere Analyzer
    }
    
    def __init__(self, parameters: List[str]):
        self.analyzers: List[BaseAnalyzer] = []
        
        for param in parameters:
            if param in self.ANALYZERS:
                self.analyzers.append(self.ANALYZERS[param]())
    
    def run(self, scenes: List[Scene]) -> List[Scene]:
        """Führt alle Analyzer sequentiell aus."""
        for analyzer in self.analyzers:
            scenes = analyzer.analyze(scenes)
        
        return scenes
```

---

## 3. FastAPI Endpoint Pattern

### Standard-Endpoint-Struktur
```python
# backend/app/api/scripts.py
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from app.services.script_service import ScriptService
from app.models.api import ScriptUploadResponse, AnalysisRequest, AnalysisResponse
from app.api.dependencies import get_script_service

router = APIRouter(prefix="/scripts", tags=["scripts"])

@router.post("/upload", response_model=ScriptUploadResponse, status_code=201)
async def upload_script(
    file: UploadFile,
    service: ScriptService = Depends(get_script_service)
):
    """
    Lädt Drehbuch hoch und führt initiales Parsing durch.
    
    Args:
        file: Hochgeladene Datei
        service: Script Service (Dependency Injection)
    
    Returns:
        Script-Metadaten
        
    Raises:
        HTTPException 400: Bei ungültigem Format
        HTTPException 413: Bei zu großer Datei
    """
    # File-Size-Check
    if file.size > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(
            status_code=413,
            detail="File too large (max 50 MB)"
        )
    
    try:
        result = await service.upload_and_parse(file)
        return result
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Error Handling Pattern
```python
# backend/app/api/error_handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.parsers.exceptions import ParsingError, UnsupportedFormatError

async def parsing_error_handler(request: Request, exc: ParsingError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "parsing_error",
            "message": str(exc),
            "detail": "Failed to parse script content"
        }
    )

async def unsupported_format_handler(request: Request, exc: UnsupportedFormatError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "unsupported_format",
            "message": str(exc),
            "supported_formats": ["fountain", "plaintext", "pdf", "fdx"]
        }
    )

# In main.py registrieren:
# app.add_exception_handler(ParsingError, parsing_error_handler)
# app.add_exception_handler(UnsupportedFormatError, unsupported_format_handler)
```

---

## 4. Pydantic Model Pattern

### Base Model mit Config
```python
# backend/app/models/base.py
from pydantic import BaseModel, ConfigDict

class BaseAPIModel(BaseModel):
    """Basis für alle API-Models."""
    
    model_config = ConfigDict(
        # JSON-Serialisierung mit CamelCase
        alias_generator=lambda field: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field.split('_'))
        ),
        populate_by_name=True,  # Erlaubt snake_case und camelCase
        from_attributes=True,  # Für ORM-Models
    )
```

### Scene Model (Domain)
```python
# backend/app/models/scene.py
from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    """Domain-Model für eine Szene."""
    
    scene_number: int = Field(ge=1, description="Szenen-Nummer (ab 1)")
    int_ext: Optional[str] = Field(None, description="INT, EXT, oder INT/EXT")
    location: Optional[str] = Field(None, max_length=200)
    time: Optional[str] = Field(None, description="TAG, NACHT, etc.")
    characters: List[str] = Field(default_factory=list)
    page_number: int = Field(ge=1)
    estimated_length: Optional[float] = Field(None, ge=0, description="Minuten")
    
    # Intern (nicht in API-Response)
    raw_content: Optional[str] = Field(None, exclude=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "scene_number": 1,
                "int_ext": "INT",
                "location": "WOHNUNG BERLIN",
                "time": "TAG",
                "characters": ["ANNA", "PETER"],
                "page_number": 1,
                "estimated_length": 2.5
            }
        }
```

---

## 5. Service Layer Pattern

### Basis-Service
```python
# backend/app/services/base.py
from abc import ABC

class BaseService(ABC):
    """Basis für alle Services."""
    
    def __init__(self, db_session=None):
        self.db = db_session
    
    def _validate_input(self, **kwargs):
        """Hook für Input-Validierung (überschreibbar)."""
        pass
```

### Script Service (Orchestration)
```python
# backend/app/services/script_service.py
from fastapi import UploadFile
from app.services.base import BaseService
from app.parsers.registry import ParserRegistry
from app.analyzers.pipeline import AnalyzerPipeline
from app.models.api import ScriptUploadResponse

class ScriptService(BaseService):
    """Service für Script-Upload und -Verarbeitung."""
    
    def __init__(self, db_session=None):
        super().__init__(db_session)
        self.parser_registry = ParserRegistry()
    
    async def upload_and_parse(self, file: UploadFile) -> ScriptUploadResponse:
        """
        Lädt Script hoch, parst es und gibt Metadaten zurück.
        """
        content = await file.read()
        
        # Parser finden
        parser = self.parser_registry.get_parser(file.filename, content)
        
        # Parsen
        scenes = parser.parse(content)
        
        # Metadaten berechnen
        pages = self._calculate_pages(scenes)
        
        return ScriptUploadResponse(
            script_id=self._generate_id(),
            filename=file.filename,
            format=parser.__class__.__name__.replace('Parser', '').lower(),
            scenes_count=len(scenes),
            pages=pages,
            upload_time=datetime.utcnow()
        )
    
    def _calculate_pages(self, scenes):
        return max(scene.page_number for scene in scenes) if scenes else 0
    
    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())
```

---

## 6. Testing Pattern

### Unit-Test für Parser
```python
# backend/tests/unit/parsers/test_fountain_parser.py
import pytest
from app.parsers.fountain_parser import FountainParser
from app.models.scene import Scene

@pytest.fixture
def fountain_parser():
    return FountainParser()

@pytest.fixture
def sample_fountain_content():
    return b"""
INT. WOHNUNG BERLIN - TAG

Anna betritt die Wohnung.

ANNA
Hallo?

PETER
(aus dem Nebenzimmer)
Hier!
"""

def test_can_parse_fountain_file(fountain_parser):
    assert fountain_parser.can_parse("script.fountain", b"INT. TEST")

def test_parse_simple_scene(fountain_parser, sample_fountain_content):
    scenes = fountain_parser.parse(sample_fountain_content)
    
    assert len(scenes) == 1
    assert scenes[0].int_ext == "INT"
    assert scenes[0].location == "WOHNUNG BERLIN"
    assert scenes[0].time == "TAG"
    assert scenes[0].scene_number == 1
```

### Integration-Test für API
```python
# backend/tests/integration/api/test_scripts.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_upload_fountain_script(client, tmp_path):
    # Sample-File erstellen
    script_file = tmp_path / "test.fountain"
    script_file.write_text("INT. TEST - TAG\n\nAction.")
    
    with open(script_file, "rb") as f:
        response = client.post(
            "/api/v1/scripts/upload",
            files={"file": ("test.fountain", f, "text/plain")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.fountain"
    assert data["format"] == "fountain"
    assert data["scenes_count"] >= 1
```

---

## 7. Frontend API-Client Pattern

### Type-Safe API-Client
```typescript
// frontend/src/lib/api.ts
const API_BASE = import.meta.env.PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Scene {
  sceneNumber: number;
  intExt?: string;
  location?: string;
  time?: string;
  characters: string[];
  pageNumber: number;
  estimatedLength?: number;
}

export interface AnalysisResponse {
  analysisId: string;
  scriptId: string;
  scenes: Scene[];
  totalScenes: number;
  totalPages: number;
  totalRuntimeEstimate: number;
}

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "APIError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json();
    throw new APIError(response.status, error.detail || "Request failed");
  }
  return response.json();
}

export async function uploadScript(file: File): Promise<{ scriptId: string }> {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${API_BASE}/scripts/upload`, {
    method: "POST",
    body: formData,
  });
  
  return handleResponse(response);
}

export async function analyzeScript(
  scriptId: string,
  parameters: string[]
): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE}/scripts/${scriptId}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ parameters }),
  });
  
  return handleResponse(response);
}
```

---

**Version**: 1.0  
**Letztes Update**: 14.10.2025  
**Nächste Erweiterung**: Nach erstem Parser-Impl
