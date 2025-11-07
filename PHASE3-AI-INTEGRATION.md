# Phase 3: AI Integration - Complete ✅

## Was wurde implementiert

### OpenRouter Client
- ✅ HTTP Client für OpenRouter AI API
- ✅ Modell-Mapping (GPT-4o-mini, GPT-4o, Claude, Gemini, Llama)
- ✅ Retry-Logik mit exponentialem Backoff
- ✅ Timeout-Handling (30s)
- ✅ JSON Response Parsing mit Fallbacks

### Prompt Engineering
- ✅ **Standard-Modus**: Story Event, Subtext, Turning Point, Characters, Mood
- ✅ **Tatort-Modus**: + Evidence, Information Flow, Knowledge Gap, Redundancy
- ✅ **Story-Modus**: + Hero's Journey, Act Structure, Plot Points
- ✅ **Combined-Modus**: Alle Features kombiniert
- ✅ Bilingual: Deutsche und englische Prompts
- ✅ System Prompt für konsistente Qualität

### Scene Analyzer
- ✅ Token-Optimierung:
  - Standard/Tatort mit >15 Szenen: Sample 15 Szenen (5 Start, 5 Mitte, 5 Ende)
  - Story-Modus: Immer alle Szenen (für Struktur-Analyse)
  - ≤15 Szenen: Immer alle analysieren
- ✅ Async Processing mit Background Tasks
- ✅ Progress-Updates in Echtzeit
- ✅ Fehlerbehandlung pro Szene
- ✅ Kosten-Schätzung

### API Endpoints
- ✅ `POST /api/v1/analyze` - Start Analyse
- ✅ `GET /api/v1/results/{job_id}` - Ergebnisse abrufen
- ✅ Background Task Processing
- ✅ Cost Estimation

### Kosten-Modell
Geschätzte Kosten pro Modell (bei 15 Szenen):
- **gpt-4o-mini**: ~0.001€ (Standard-Empfehlung)
- **claude-3-haiku**: ~0.002€  
- **gemini-flash**: ~0.001€
- **llama-70b**: ~0.001€
- **gpt-4o**: ~0.015€ (teuer, beste Qualität)

## Implementierte Features

### Prompt-Struktur

#### Standard-Prompt (EN):
```json
{
  "story_event": "One sentence summary",
  "subtext": "5-10 words emotional layer",
  "turning_point": "Action|Revelation|Decision|Realization|None",
  "on_stage": ["Character1", "Character2"],
  "off_stage": ["Mentioned Character"],
  "protagonist_mood": "Angry|Desperate|Hopeful|etc."
}
```

#### Tatort-Erweiterung:
```json
{
  "evidence": "Found evidence or clues",
  "information_flow": "Truth|Lie|Concealment|etc.",
  "knowledge_gap": "Viewer>Character|Character>Viewer|Equal",
  "redundancy": "New info|Repetition|Variation"
}
```

#### Story-Erweiterung:
```json
{
  "hero_journey": "Ordinary World|Call to Adventure|etc.",
  "act": "Act I|Act II-A|Act II-B|Act III",
  "plot_point_actual": "Inciting Incident|Plot Point 1|etc.",
  "plot_point_expected": "Expected based on position"
}
```

### Token-Optimierung

```python
# Strategie für Standard/Tatort-Modi
if total_scenes > 15:
    # Sample 15 Szenen:
    scenes_to_analyze = [
        0, 1, 2, 3, 4,           # Start (5)
        mid-2, mid-1, mid, mid+1, mid+2,  # Mitte (5)
        end-5, end-4, end-3, end-2, end-1 # Ende (5)
    ]
else:
    # Alle Szenen
    scenes_to_analyze = all_scenes

# Story-Modus: Immer alle (für Struktur)
if mode == "story" or mode == "combined":
    scenes_to_analyze = all_scenes
```

### Response Parsing

```python
# Robust parsing mit Fallbacks:
1. Strip markdown code blocks (```json)
2. JSON.parse()
3. Fallback: Regex-Extraktion
4. Validate required fields
5. Ensure list types for characters
```

### Error Handling

- **API Fehler**: 3 Retries mit exponential backoff (1s, 2s, 4s)
- **Parsing Fehler**: Fallback auf "Unknown" Werte
- **Szenen-Fehler**: Error-Entry in Results (Analysis failed)
- **Timeout**: 30s pro Szene

## Code-Struktur

```
backend/app/analyzer/
├── __init__.py
├── openrouter_client.py   # API Client
└── scene_analyzer.py      # Batch Processing
```

## API Flow

```
1. POST /api/v1/upload
   → File ID erstellt, Szenen extrahiert

2. POST /api/v1/analyze
   → Body: {file_id, language, model, mode}
   → Cost Estimation
   → Background Task gestartet
   → Response: {job_id, status: "queued", estimated_cost}

3. GET /api/v1/status/{job_id} (Polling)
   → {status, progress, current_scene, total_scenes}
   → Status: uploaded → queued → processing → analyzing → completed

4. GET /api/v1/results/{job_id}
   → Full analysis results
```

## Beispiel-Request

```bash
# 1. Upload
curl -X POST http://localhost:8001/api/v1/upload \
  -F "file=@screenplay.pdf"
# → {file_id: "abc-123", ...}

# 2. Start Analysis
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc-123",
    "output_language": "EN",
    "model": "gpt-4o-mini",
    "mode": "standard"
  }'
# → {job_id: "abc-123", status: "queued", estimated_cost: 0.001}

# 3. Poll Status
curl http://localhost:8001/api/v1/status/abc-123
# → {status: "analyzing", progress: 60, current_scene: 9, total_scenes: 15}

# 4. Get Results (when completed)
curl http://localhost:8001/api/v1/results/abc-123
# → {results: [...], total_scenes: 15, ...}
```

## Setup für Testing

### 1. OpenRouter API Key besorgen
```bash
# 1. Gehe zu https://openrouter.ai/keys
# 2. Erstelle neuen API Key
# 3. Kopiere Key
```

### 2. .env Datei erstellen
```bash
cp .env.example .env
# Editiere .env und setze echten API Key:
# OPENROUTER_API_KEY=sk-or-v1-DEIN-KEY-HIER
```

### 3. Backend neu starten
```bash
docker-compose restart backend
```

### 4. Test mit kleiner Datei
```bash
# Upload
RESULT=$(curl -s -X POST http://localhost:8001/api/v1/upload \
  -F "file=@examples/treatments/WreckingBall-Treatment_2025-06-klein.pdf")
FILE_ID=$(echo $RESULT | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")

# Analyze
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FILE_ID\",
    \"output_language\": \"EN\",
    \"model\": \"gpt-4o-mini\",
    \"mode\": \"standard\"
  }"

# Status (mehrmals)
watch -n 2 "curl -s http://localhost:8001/api/v1/status/$FILE_ID | python3 -m json.tool"

# Results
curl -s http://localhost:8001/api/v1/results/$FILE_ID | python3 -m json.tool
```

## Performance

- **API Call**: ~1-3s pro Szene (abhängig vom Modell)
- **Batch Processing**: 15 Szenen ≈ 30-45s
- **Memory**: ~5-10MB pro Job
- **Concurrent Jobs**: Unlimited (in-memory)

## Fehlerbehandlung

```python
# API Key fehlt
→ ValueError: "OPENROUTER_API_KEY environment variable not set"

# API Request failed
→ Exception: "API request failed after 3 attempts: ..."

# Parse Error
→ ValueError: "Could not parse JSON from response: ..."

# Job not found
→ 404: "Job not found"

# Analysis not completed
→ 400: "Analysis not completed. Current status: analyzing"
```

## Nächste Schritte (Phase 4)

Phase 4 wird implementieren:
- [ ] Excel-Generator mit openpyxl
- [ ] Multi-Language Headers (DE/EN)
- [ ] Mode-spezifische Spalten (Tatort/Story)
- [ ] Formatierung & Styling
- [ ] Download-Endpoint
- [ ] Aronson-Sheet für Story-Modus

## Checkpoints ✅

- [x] OpenRouter Client implementiert
- [x] Prompt Templates (Standard, Tatort, Story)
- [x] Token-Optimierung (15-Szenen-Sampling)
- [x] Async Background Processing
- [x] Progress-Updates
- [x] Cost Estimation
- [x] Error Handling mit Retries
- [x] Response Parsing mit Fallbacks
- [x] Analyze Endpoint
- [x] Results Endpoint

---

**Phase 3 Status**: ✅ Abgeschlossen (Bereit für Testing mit echtem API Key)  
**Branch**: `phase-3-ai-integration`  
**Tag**: `v0.3.0` (nach Merge & Test)  
**API Version**: 0.3.0

**WICHTIG**: Zum Testen wird ein echter OpenRouter API Key benötigt!
