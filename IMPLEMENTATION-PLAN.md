# 🚀 Scene Analyzer - Implementierungsplan

## Übersicht
Schritt-für-Schritt Anleitung zur Umsetzung des Scene Analyzer MVPs.
**Geschätzte Gesamtdauer**: 5-7 Tage bei fokussierter Arbeit

## 📌 Git-Strategie

### Branch-Struktur
```
main
├── phase-1-docker-setup
├── phase-2-backend-core
├── phase-3-ai-integration
├── phase-4-excel-generation
├── phase-5-frontend
└── phase-6-integration
```

### Workflow pro Phase
1. **Neue Branch erstellen**: `git checkout -b phase-X-name`
2. **Entwicklung & Commits**: Regelmäßige Commits mit aussagekräftigen Messages
3. **Push zu GitHub**: `git push -u origin phase-X-name`
4. **Pull Request**: Nach Abschluss der Phase
5. **Merge zu main**: Nach Review/Test
6. **Tag erstellen**: `git tag -a v0.X.0 -m "Phase X completed"`

### Initial Setup (einmalig)
```bash
# GitHub Repository erstellen (falls noch nicht vorhanden)
git init
git remote add origin https://github.com/johanneshoss/scene-analyzer.git

# Initial commit
git add .
git commit -m "feat: Initial project setup with documentation"
git push -u origin main
```

---

## Phase 1: Docker & Basis-Setup (Tag 1)

### Git Setup für Phase 1
```bash
# Branch erstellen
git checkout -b phase-1-docker-setup

# Nach Abschluss
git add .
git commit -m "feat(docker): Complete Docker setup with compose and containers"
git push -u origin phase-1-docker-setup

# PR erstellen und mergen, dann:
git checkout main
git pull
git tag -a v0.1.0 -m "Phase 1: Docker infrastructure complete"
git push --tags
```

### 1.1 Docker Compose erstellen
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8001:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./backend/app:/app
    networks:
      - scene-network

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - scene-network

networks:
  scene-network:
    driver: bridge
```

### 1.2 Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 1.3 Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY static/ /usr/share/nginx/html/

EXPOSE 80
```

### 1.4 Environment Setup
```bash
# .env erstellen
echo "OPENROUTER_API_KEY=sk-or-v1-xxxxx" > .env

# .gitignore erweitern
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 1.5 Requirements definieren
```txt
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pypdf2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
pydantic==2.5.0
requests==2.31.0
aiofiles==23.2.1
python-jose[cryptography]==3.3.0
```

**✅ Checkpoint**: `docker-compose up` sollte beide Container starten

---

## Phase 2: Backend Core API (Tag 1-2)

### Git Setup für Phase 2
```bash
# Branch erstellen
git checkout -b phase-2-backend-core

# Nach Abschluss
git add .
git commit -m "feat(backend): Implement core API with upload and parsing"
git push -u origin phase-2-backend-core

# PR erstellen und mergen, dann:
git checkout main
git pull
git tag -a v0.2.0 -m "Phase 2: Backend core API complete"
git push --tags
```

### 2.1 FastAPI Grundgerüst
```python
# backend/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Optional, Dict, List
import os

app = FastAPI(title="Scene Analyzer API", version="1.0.0")

# CORS für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Storage
analysis_jobs: Dict[str, dict] = {}

class AnalysisRequest(BaseModel):
    file_id: str
    output_language: str  # "DE" oder "EN"
    model: str  # "gpt-4o-mini", "gpt-4o", etc.
    mode: str  # "standard", "tatort", "story", "combined"
    protagonist_count: Optional[int] = 1

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """Datei hochladen und validieren"""
    # Validierung
    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(400, "File too large")
    
    allowed_types = [".pdf", ".docx", ".txt"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file_ext}")
    
    # File ID generieren
    file_id = str(uuid.uuid4())
    
    # In Memory speichern
    content = await file.read()
    analysis_jobs[file_id] = {
        "filename": file.filename,
        "content": content,
        "status": "uploaded",
        "file_type": file_ext
    }
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "size": len(content)
    }

@app.post("/api/v1/analyze")
async def start_analysis(request: AnalysisRequest):
    """Analyse starten"""
    if request.file_id not in analysis_jobs:
        raise HTTPException(404, "File not found")
    
    job = analysis_jobs[request.file_id]
    job.update({
        "status": "processing",
        "output_language": request.output_language,
        "model": request.model,
        "mode": request.mode,
        "progress": 0,
        "total_scenes": 0
    })
    
    # TODO: Async Task starten
    # asyncio.create_task(process_analysis(request.file_id))
    
    return {"job_id": request.file_id, "status": "started"}

@app.get("/api/v1/status/{job_id}")
async def get_status(job_id: str):
    """Status abfragen"""
    if job_id not in analysis_jobs:
        raise HTTPException(404, "Job not found")
    
    job = analysis_jobs[job_id]
    return {
        "status": job["status"],
        "progress": job.get("progress", 0),
        "total_scenes": job.get("total_scenes", 0),
        "error": job.get("error")
    }
```

### 2.2 Parser Module erstellen
```python
# backend/app/parsers/__init__.py
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TXTParser

def get_parser(file_type: str):
    parsers = {
        ".pdf": PDFParser,
        ".docx": DOCXParser,
        ".txt": TXTParser
    }
    return parsers.get(file_type)
```

### 2.3 PDF Parser
```python
# backend/app/parsers/pdf_parser.py
import PyPDF2
from typing import List, Dict
import re

class PDFParser:
    def __init__(self, content: bytes):
        self.content = content
    
    def extract_text(self) -> str:
        """Extrahiere Text aus PDF"""
        # Implementation mit PyPDF2
        pass
    
    def extract_scenes(self) -> List[Dict]:
        """Erkenne und extrahiere Szenen"""
        text = self.extract_text()
        scenes = []
        
        # Slugline Pattern (INT./EXT.)
        slugline_pattern = r'^(INT\.|EXT\.|INT/EXT\.)(.+?)(?:[-–](.+?))?$'
        
        # Text in Szenen aufteilen
        # ... Implementation
        
        return scenes
```

**✅ Checkpoint**: Upload-Endpoint funktioniert, Dateien werden validiert

---

## Phase 3: AI Integration (Tag 2-3)

### Git Setup für Phase 3
```bash
# Branch erstellen
git checkout -b phase-3-ai-integration

# Nach Abschluss
git add .
git commit -m "feat(ai): Integrate OpenRouter API for scene analysis"
git push -u origin phase-3-ai-integration

# PR erstellen und mergen, dann:
git checkout main
git pull
git tag -a v0.3.0 -m "Phase 3: AI integration complete"
git push --tags
```

### 3.1 OpenRouter Client
```python
# backend/app/analyzer/openrouter_client.py
import requests
import os
from typing import Dict, List

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        self.models = {
            "gpt-4o-mini": "openai/gpt-4o-mini",
            "gpt-4o": "openai/gpt-4o",
            "claude-3-haiku": "anthropic/claude-3-haiku",
            "gemini-flash": "google/gemini-1.5-flash",
            "llama-70b": "meta-llama/llama-3.1-70b"
        }
    
    def analyze_scene(self, scene_text: str, mode: str, language: str, model: str) -> Dict:
        """Einzelne Szene analysieren"""
        prompt = self._build_prompt(scene_text, mode, language)
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.models[model],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
        )
        
        # Parse response und strukturiere Daten
        return self._parse_response(response.json())
    
    def _build_prompt(self, scene: str, mode: str, language: str) -> str:
        """Prompt basierend auf Modus erstellen"""
        base_prompt = f"""
        Analysiere diese Szene und extrahiere folgende Informationen:
        
        SZENE:
        {scene}
        
        AUSGABE (als JSON):
        - story_event: (1 Satz Zusammenfassung)
        - subtext: (5-10 Wörter emotionale Ebene)
        - turning_point: (Action/Revelation/Decision/Realization/None)
        - on_stage: (Liste anwesender Charaktere)
        - off_stage: (Liste erwähnter Charaktere)
        - protagonist_mood: (Emotional state)
        """
        
        if mode in ["tatort", "combined"]:
            base_prompt += """
            - evidence: (Gefundene Beweise)
            - information_flow: (Wahrheit/Lüge/Verschweigen)
            - knowledge_gap: (Zuschauer>Figur/Figur>Zuschauer/Gleichstand)
            - redundancy: (Neue Info/Wiederholung)
            """
        
        return base_prompt
```

### 3.2 Szenen-Analyzer
```python
# backend/app/analyzer/scene_analyzer.py
from typing import List, Dict
import asyncio

class SceneAnalyzer:
    def __init__(self, client, mode: str, language: str, model: str):
        self.client = client
        self.mode = mode
        self.language = language
        self.model = model
    
    async def analyze_all_scenes(self, scenes: List[Dict], job_id: str) -> List[Dict]:
        """Alle Szenen analysieren mit Progress-Updates"""
        results = []
        total = len(scenes)
        
        # Token-Optimierung
        if self.mode in ["standard", "tatort"] and total > 15:
            # Sample: 5 Anfang, 5 Mitte, 5 Ende
            sample_indices = (
                list(range(5)) + 
                list(range(total//2 - 2, total//2 + 3)) + 
                list(range(total - 5, total))
            )
            scenes_to_analyze = [scenes[i] for i in sample_indices]
        else:
            scenes_to_analyze = scenes
        
        for i, scene in enumerate(scenes_to_analyze):
            # Analyse
            result = await self.client.analyze_scene(
                scene['text'], 
                self.mode, 
                self.language,
                self.model
            )
            
            # Progress Update
            progress = int((i + 1) / len(scenes_to_analyze) * 100)
            # Update job progress in memory
            
            results.append({
                "scene_number": scene['number'],
                **result
            })
        
        return results
```

**✅ Checkpoint**: OpenRouter API verbunden, erste Szene kann analysiert werden

---

## Phase 4: Excel Generation (Tag 3-4)

### Git Setup für Phase 4
```bash
# Branch erstellen
git checkout -b phase-4-excel-generation

# Nach Abschluss
git add .
git commit -m "feat(excel): Implement Excel generator with multi-language support"
git push -u origin phase-4-excel-generation

# PR erstellen und mergen, dann:
git checkout main
git pull
git tag -a v0.4.0 -m "Phase 4: Excel generation complete"
git push --tags
```

### 4.1 Excel Generator
```python
# backend/app/excel/generator.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List, Dict
import io

class ExcelGenerator:
    def __init__(self, language: str, mode: str):
        self.language = language
        self.mode = mode
        self.wb = Workbook()
        
    def generate(self, analysis_data: List[Dict]) -> bytes:
        """Excel-Datei generieren"""
        ws = self.wb.active
        ws.title = "Szenen-Analyse"
        
        # Headers definieren
        headers = self._get_headers()
        
        # Header-Zeile formatieren
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="E0E0E0")
            cell.alignment = Alignment(horizontal="center")
        
        # Daten einfügen
        for row, scene in enumerate(analysis_data, 2):
            for col, key in enumerate(self._get_data_keys(), 1):
                ws.cell(row=row, column=col, value=scene.get(key, ""))
        
        # Auto-Width für Spalten
        for column in ws.columns:
            max_length = 0
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
        
        # Bei Story-Modus: Zweites Sheet für Aronson
        if "story" in self.mode:
            self._add_aronson_sheet(analysis_data)
        
        # Als Bytes speichern
        buffer = io.BytesIO()
        self.wb.save(buffer)
        return buffer.getvalue()
    
    def _get_headers(self) -> List[str]:
        """Header basierend auf Sprache und Modus"""
        if self.language == "DE":
            headers = [
                "Szenennummer", "INT/EXT", "Schauplatz", "Tageszeit",
                "Story Event", "Subtext", "Wendepunkt", 
                "Anwesend", "Erwähnt", "Anzahl", "Stimmung Protagonist"
            ]
            if "tatort" in self.mode:
                headers.extend([
                    "Beweismittel", "Informationsfluss", 
                    "Wissensvorsprung", "Redundanz-Check"
                ])
        else:  # EN
            headers = [
                "Scene Number", "INT/EXT", "Location", "Time of Day",
                "Story Event", "Subtext", "Turning Point",
                "On Stage", "Off Stage", "Character Count", "Protagonist Mood"
            ]
            if "tatort" in self.mode:
                headers.extend([
                    "Evidence", "Information Flow",
                    "Knowledge Gap", "Redundancy Check"
                ])
        
        if "story" in self.mode:
            if self.language == "DE":
                headers.extend(["Hero's Journey", "Akt", "Plot Point (Ist)", "Plot Point (Soll)"])
            else:
                headers.extend(["Hero's Journey", "Act", "Plot Point (Actual)", "Plot Point (Expected)"])
        
        return headers
    
    def _add_aronson_sheet(self, data: List[Dict]):
        """Aronson Analyse Sheet hinzufügen"""
        ws = self.wb.create_sheet("Aronson Analyse")
        
        questions = self._get_aronson_questions()
        
        # Fragen und Antworten
        for row, (question, answer) in enumerate(questions, 1):
            ws.cell(row=row, column=1, value=question).font = Font(bold=True)
            ws.cell(row=row, column=2, value=answer)
        
        # Formatierung
        ws.column_dimensions['A'].width = 60
        ws.column_dimensions['B'].width = 80
```

**✅ Checkpoint**: Excel-Datei wird generiert mit korrekten Headers

---

## Phase 5: Frontend Implementation (Tag 4-5)

### Git Setup für Phase 5
```bash
# Branch erstellen
git checkout -b phase-5-frontend

# Nach Abschluss
git add .
git commit -m "feat(frontend): Implement step-wizard UI with Tailwind"
git push -u origin phase-5-frontend

# PR erstellen und mergen, dann:
git checkout main
git pull
git tag -a v0.5.0 -m "Phase 5: Frontend UI complete"
git push --tags
```

### 5.1 HTML Struktur
```html
<!-- frontend/static/index.html -->
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scene Analyzer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 font-[Inter]">
    <!-- Language Toggle -->
    <div class="absolute top-4 right-4">
        <button id="langToggle" class="px-4 py-2 bg-white rounded-lg shadow">
            DE / EN
        </button>
    </div>

    <!-- Main Container -->
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Scene Analyzer</h1>
        
        <!-- Progress Steps -->
        <div class="mb-8">
            <div class="flex justify-between">
                <div class="step active" data-step="1">Upload</div>
                <div class="step" data-step="2">Sprache</div>
                <div class="step" data-step="3">Modell</div>
                <div class="step" data-step="4">Modus</div>
                <div class="step" data-step="5">Bestätigung</div>
            </div>
        </div>

        <!-- Step Content -->
        <div id="stepContent" class="bg-white rounded-xl shadow-lg p-8">
            <!-- Step 1: Upload -->
            <div id="step1" class="step-content">
                <div id="dropZone" class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center cursor-pointer hover:border-indigo-600 transition">
                    <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p class="text-gray-600 mb-2">Datei hier ablegen oder klicken zum Auswählen</p>
                    <p class="text-sm text-gray-400">PDF, DOCX oder TXT (max. 50MB)</p>
                </div>
                <input type="file" id="fileInput" class="hidden" accept=".pdf,.docx,.txt">
                <div id="fileInfo" class="mt-4 hidden">
                    <p class="text-sm text-gray-600">Ausgewählte Datei: <span id="fileName" class="font-medium"></span></p>
                </div>
            </div>

            <!-- Step 2: Sprache -->
            <div id="step2" class="step-content hidden">
                <h3 class="text-lg font-semibold mb-4">Ausgabesprache wählen</h3>
                <div class="space-y-3">
                    <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="language" value="DE" class="mr-3">
                        <span>Deutsch</span>
                    </label>
                    <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="language" value="EN" class="mr-3">
                        <span>English</span>
                    </label>
                </div>
            </div>

            <!-- Step 3: Modell -->
            <div id="step3" class="step-content hidden">
                <h3 class="text-lg font-semibold mb-4">AI-Modell auswählen</h3>
                <select id="modelSelect" class="w-full p-3 border rounded-lg">
                    <option value="gpt-4o-mini">GPT-4o-mini (Schnell & Günstig)</option>
                    <option value="gpt-4o">GPT-4o (Beste Qualität)</option>
                    <option value="claude-3-haiku">Claude 3 Haiku (Sehr schnell)</option>
                    <option value="gemini-flash">Gemini 1.5 Flash (Google)</option>
                    <option value="llama-70b">Llama 3.1 70B (Open Source)</option>
                </select>
            </div>

            <!-- Step 4: Modus -->
            <div id="step4" class="step-content hidden">
                <h3 class="text-lg font-semibold mb-4">Analyse-Modus wählen</h3>
                <div class="space-y-3">
                    <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="mode" value="standard" class="mr-3">
                        <div>
                            <p class="font-medium">Standard</p>
                            <p class="text-sm text-gray-500">Basis-Szenenanalyse</p>
                        </div>
                    </label>
                    <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="mode" value="tatort" class="mr-3">
                        <div>
                            <p class="font-medium">Tatort</p>
                            <p class="text-sm text-gray-500">+ Krimi-spezifische Analyse</p>
                        </div>
                    </label>
                    <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="mode" value="story" class="mr-3">
                        <div>
                            <p class="font-medium">Story (Beta)</p>
                            <p class="text-sm text-gray-500">+ Struktur-Analyse</p>
                        </div>
                    </label>
                    <label class="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                        <input type="radio" name="mode" value="combined" class="mr-3">
                        <div>
                            <p class="font-medium">Kombiniert</p>
                            <p class="text-sm text-gray-500">Tatort + Story</p>
                        </div>
                    </label>
                </div>
            </div>

            <!-- Step 5: Bestätigung -->
            <div id="step5" class="step-content hidden">
                <h3 class="text-lg font-semibold mb-4">Zusammenfassung</h3>
                <div class="bg-gray-50 p-4 rounded-lg space-y-2">
                    <p><span class="font-medium">Datei:</span> <span id="summaryFile"></span></p>
                    <p><span class="font-medium">Sprache:</span> <span id="summaryLang"></span></p>
                    <p><span class="font-medium">Modell:</span> <span id="summaryModel"></span></p>
                    <p><span class="font-medium">Modus:</span> <span id="summaryMode"></span></p>
                </div>
                <div class="mt-6 p-4 bg-indigo-50 rounded-lg">
                    <p class="text-sm font-medium text-indigo-900">Geschätzte Kosten:</p>
                    <p class="text-2xl font-bold text-indigo-600" id="costEstimate">~0.50€</p>
                </div>
            </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between mt-8">
            <button id="prevBtn" class="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg disabled:opacity-50" disabled>
                Zurück
            </button>
            <button id="nextBtn" class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                Weiter
            </button>
        </div>
    </div>

    <!-- Progress Modal -->
    <div id="progressModal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center">
        <div class="bg-white rounded-xl p-8 max-w-md w-full">
            <h3 class="text-lg font-semibold mb-4">Analyse läuft...</h3>
            <div class="mb-4">
                <div class="bg-gray-200 rounded-full h-3">
                    <div id="progressBar" class="bg-indigo-600 h-3 rounded-full transition-all" style="width: 0%"></div>
                </div>
            </div>
            <p class="text-sm text-gray-600">
                Szene <span id="currentScene">0</span> von <span id="totalScenes">0</span>
            </p>
            <p class="text-xs text-gray-500 mt-2">
                Geschätzte Restzeit: <span id="remainingTime">Berechne...</span>
            </p>
            <button id="cancelBtn" class="mt-4 w-full px-4 py-2 bg-red-600 text-white rounded-lg">
                Abbrechen
            </button>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

### 5.2 JavaScript Logic
```javascript
// frontend/static/app.js
class SceneAnalyzer {
    constructor() {
        this.currentStep = 1;
        this.fileId = null;
        this.jobId = null;
        this.data = {
            file: null,
            language: 'DE',
            model: 'gpt-4o-mini',
            mode: 'standard'
        };
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // File Upload
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-indigo-600');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });
        
        // Navigation
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('prevBtn').addEventListener('click', () => this.prevStep());
    }
    
    async handleFile(file) {
        this.data.file = file;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileInfo').classList.remove('hidden');
        
        // Upload file
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('http://localhost:8001/api/v1/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            this.fileId = result.file_id;
        } catch (error) {
            console.error('Upload failed:', error);
        }
    }
    
    nextStep() {
        if (this.currentStep === 5) {
            this.startAnalysis();
            return;
        }
        
        // Daten sammeln
        if (this.currentStep === 2) {
            this.data.language = document.querySelector('input[name="language"]:checked')?.value || 'DE';
        }
        if (this.currentStep === 3) {
            this.data.model = document.getElementById('modelSelect').value;
        }
        if (this.currentStep === 4) {
            this.data.mode = document.querySelector('input[name="mode"]:checked')?.value || 'standard';
        }
        
        this.currentStep++;
        this.updateUI();
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateUI();
        }
    }
    
    updateUI() {
        // Hide all steps
        document.querySelectorAll('.step-content').forEach(el => el.classList.add('hidden'));
        // Show current step
        document.getElementById(`step${this.currentStep}`).classList.remove('hidden');
        
        // Update navigation
        document.getElementById('prevBtn').disabled = this.currentStep === 1;
        document.getElementById('nextBtn').textContent = this.currentStep === 5 ? 'Analyse starten' : 'Weiter';
        
        // Update progress indicators
        document.querySelectorAll('.step').forEach((step, index) => {
            step.classList.toggle('active', index + 1 <= this.currentStep);
        });
        
        // Update summary on step 5
        if (this.currentStep === 5) {
            document.getElementById('summaryFile').textContent = this.data.file?.name || '';
            document.getElementById('summaryLang').textContent = this.data.language;
            document.getElementById('summaryModel').textContent = this.data.model;
            document.getElementById('summaryMode').textContent = this.data.mode;
        }
    }
    
    async startAnalysis() {
        // Show progress modal
        document.getElementById('progressModal').classList.remove('hidden');
        document.getElementById('progressModal').classList.add('flex');
        
        // Start analysis
        const response = await fetch('http://localhost:8001/api/v1/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: this.fileId,
                output_language: this.data.language,
                model: this.data.model,
                mode: this.data.mode
            })
        });
        
        const result = await response.json();
        this.jobId = result.job_id;
        
        // Poll for status
        this.pollStatus();
    }
    
    async pollStatus() {
        const interval = setInterval(async () => {
            const response = await fetch(`http://localhost:8001/api/v1/status/${this.jobId}`);
            const status = await response.json();
            
            // Update progress
            document.getElementById('progressBar').style.width = `${status.progress}%`;
            document.getElementById('currentScene').textContent = status.current_scene || 0;
            document.getElementById('totalScenes').textContent = status.total_scenes || 0;
            
            if (status.status === 'completed') {
                clearInterval(interval);
                this.downloadResult();
            } else if (status.status === 'error') {
                clearInterval(interval);
                alert('Fehler: ' + status.error);
            }
        }, 1000);
    }
    
    async downloadResult() {
        window.location.href = `http://localhost:8001/api/v1/download/${this.jobId}`;
        document.getElementById('progressModal').classList.add('hidden');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new SceneAnalyzer();
});
```

---

## Phase 6: Integration & Testing (Tag 5)

### Git Setup für Phase 6
```bash
# Branch erstellen
git checkout -b phase-6-integration

# Nach Abschluss
git add .
git commit -m "feat(integration): Complete end-to-end integration and testing"
git push -u origin phase-6-integration

# PR erstellen und mergen, dann:
git checkout main
git pull
git tag -a v1.0.0 -m "MVP Release: Scene Analyzer v1.0.0"
git push --tags
```

### 6.1 Vollständige Backend-Integration
```python
# backend/app/main.py - Erweitert
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

async def process_analysis(job_id: str):
    """Kompletter Analyse-Prozess"""
    try:
        job = analysis_jobs[job_id]
        
        # 1. Parser wählen und Text extrahieren
        parser_class = get_parser(job['file_type'])
        parser = parser_class(job['content'])
        scenes = parser.extract_scenes()
        
        job['total_scenes'] = len(scenes)
        job['status'] = 'analyzing'
        
        # 2. AI-Analyse
        client = OpenRouterClient()
        analyzer = SceneAnalyzer(
            client, 
            job['mode'], 
            job['output_language'],
            job['model']
        )
        
        results = await analyzer.analyze_all_scenes(scenes, job_id)
        
        # 3. Excel generieren
        generator = ExcelGenerator(job['output_language'], job['mode'])
        excel_data = generator.generate(results)
        
        job['result'] = excel_data
        job['status'] = 'completed'
        
    except Exception as e:
        job['status'] = 'error'
        job['error'] = str(e)

@app.get("/api/v1/download/{job_id}")
async def download_result(job_id: str):
    """Excel-Datei downloaden"""
    if job_id not in analysis_jobs:
        raise HTTPException(404, "Job not found")
    
    job = analysis_jobs[job_id]
    if job['status'] != 'completed':
        raise HTTPException(400, "Analysis not completed")
    
    return Response(
        content=job['result'],
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f'attachment; filename="{job["filename"]}_analyse.xlsx"'
        }
    )
```

### 6.2 Nginx Konfiguration
```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📋 Git Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>
```

### Types
- **feat**: Neue Funktion
- **fix**: Bugfix
- **docs**: Dokumentation
- **style**: Formatierung
- **refactor**: Code-Umstrukturierung
- **test**: Tests
- **chore**: Wartungsarbeiten

### Beispiele
```bash
git commit -m "feat(parser): Add PDF scene extraction logic"
git commit -m "fix(api): Handle file upload validation errors"
git commit -m "docs: Update CLAUDE.md with latest architecture changes"
```

## 🚀 Launch Checklist

### Vor dem Start
- [ ] `.env` Datei mit OpenRouter API Key erstellt
- [ ] Docker Desktop läuft
- [ ] Alle Dateien an richtiger Stelle

### Start-Kommandos
```bash
# 1. Container bauen und starten
docker-compose build
docker-compose up

# 2. Browser öffnen
open http://localhost:3000

# 3. Logs beobachten (in neuem Terminal)
docker-compose logs -f backend
```

### Test-Szenario
1. [ ] Beispiel-PDF aus `examples/` hochladen
2. [ ] Deutsch als Ausgabesprache wählen
3. [ ] GPT-4o-mini als Modell wählen
4. [ ] Standard-Modus wählen
5. [ ] Analyse starten
6. [ ] Excel-Download prüfen

### Troubleshooting
- **Upload schlägt fehl**: CORS-Settings prüfen
- **Analyse hängt**: OpenRouter API Key prüfen
- **Excel leer**: Parser-Output debuggen
- **Frontend nicht erreichbar**: Nginx-Logs prüfen

---

## 📊 Erwartete Ergebnisse

Nach erfolgreicher Implementierung sollte das System:
1. ✅ PDFs, DOCX und TXT-Dateien akzeptieren
2. ✅ Szenen automatisch erkennen und extrahieren
3. ✅ Jede Szene via AI analysieren
4. ✅ Formatierte Excel-Datei generieren
5. ✅ Progress in Echtzeit anzeigen
6. ✅ Kosten transparent darstellen
7. ✅ Mehrere Analyse-Modi unterstützen
8. ✅ DE/EN Ausgabe ermöglichen

---

## 🎯 Nächste Schritte (nach MVP)

1. **Performance-Optimierung**
   - Caching für wiederholte Analysen
   - Parallele Verarbeitung mehrerer Dateien
   
2. **Feature-Erweiterungen**
   - Weitere Dateiformate (Final Draft .fdx)
   - Zusätzliche Analyse-Modi
   - Batch-Upload Interface
   
3. **Deployment-Optionen**
   - Docker Registry Push
   - Cloud Deployment Guide
   - Kubernetes Manifests

---

*Stand: November 2024 - Version 1.0*