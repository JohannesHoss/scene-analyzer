# CLAUDE.md - AI System Reference Documentation

## 🤖 Document Purpose
This document serves as a comprehensive system reference for future AI agents working on the Scene Analyzer project. It contains critical architectural decisions, implementation patterns, and system knowledge that should be preserved across sessions.

**Last Updated**: November 6, 2025
**AI Agent**: Claude 4.1 Opus via Warp

---

## 🎯 Project Overview

**Scene Analyzer** is a fully automated screenplay and treatment analysis tool that:
- Accepts screenplay/treatment uploads (PDF, DOCX, TXT)
- Performs AI-powered scene analysis using OpenRouter API
- Generates detailed Excel reports with scene breakdowns
- Supports German and English (auto-detection for input, user selection for output)
- Runs locally via Docker on Mac/Windows/Linux

### Core Value Proposition
Upload a screenplay → Receive detailed Excel analysis with minimal user interaction

---

## 🏗️ System Architecture

### Container Architecture
```
Docker Compose Setup:
├── Backend Container (Python/FastAPI) - Port 8001
├── Frontend Container (Nginx) - Port 3000
└── Bridge Network (Internal Communication)
```

### No Database Design
- **Stateless architecture** - all processing is in-memory
- No user accounts or session persistence
- Files are processed and immediately discarded after download
- Cost-effective and privacy-focused approach

### Project Structure
```
scene-analyzer/
├── CLAUDE.md              # This file - AI reference documentation
├── scene-analyzer.md      # Project specifications and requirements
├── docker-compose.yml     # Container orchestration
├── .env                   # API Keys (gitignored)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py        # FastAPI application
│       ├── parsers/       # PDF/DOCX/TXT parsing logic
│       ├── analyzer/      # AI analysis logic
│       └── excel/         # Excel generation
├── frontend/
│   ├── Dockerfile
│   └── static/
│       ├── index.html     # Upload UI
│       ├── app.js         # Frontend logic
│       └── styles.css     # (Uses Tailwind CDN)
└── examples/              # Test documents
    ├── screenplays/       # Sample screenplays
    └── treatments/        # Sample treatments
```

---

## 🔧 Technical Stack

### Backend (Port 8001)
- **Python 3.12+** with **FastAPI**
- **Key Libraries**:
  - `pypdf2` - PDF parsing
  - `python-docx` - DOCX parsing
  - `requests` - OpenRouter API client
  - `openpyxl` - Excel generation
  - `pydantic` - Type validation
  - `python-multipart` - File upload handling

### Frontend (Port 3000)
- **Nginx** - Static file server
- **Vanilla JavaScript** - No framework, no build process
- **Tailwind CSS** via CDN - Styling
- **Light Mode Only** - Simplified UI

### AI Integration
- **OpenRouter API** - Model aggregator
- **Available Models**:
  - GPT-4o-mini (default - fast & cheap)
  - GPT-4o (full power, expensive)
  - Claude 3 Haiku (very fast, very cheap)
  - Gemini 1.5 Flash (Google, cheap)
  - Llama 3.1 70B (open source alternative)

---

## 🔄 Core Workflows

### 1. File Processing Pipeline
```
Upload → Validation → Format Detection → Scene Extraction → AI Analysis → Excel Generation → Download
```

### 2. Scene Detection Logic
**For Screenplays** (with sluglines):
- Primary: INT./EXT. sluglines
- Secondary: Scene headers

**For Treatments** (without clear sluglines):
1. Time jumps: "Later", "Next day" → new scene
2. Location changes: "Meanwhile at..." → new scene
3. Double line breaks → possible scene change
4. Fallback: Auto-split after ~300-500 words

### 3. Analysis Modes

#### Standard Mode
Basic scene analysis with:
- Scene metadata (INT/EXT, Location, Time)
- Story Event (1-sentence summary)
- Subtext (emotional undertone)
- Character tracking
- Protagonist mood

#### Tatort Mode (Crime/Detective)
Standard + additional columns:
- Evidence tracking
- Information flow (truth/lie/omission)
- Knowledge gaps (viewer vs characters)
- Redundancy checking

#### Story Mode Beta
Standard + structural analysis:
- Hero's Journey stages
- Act structure mapping
- Plot point identification
- **Sheet 2**: Linda Aronson's method analysis (10 core questions)

---

## 📊 Excel Output Structure

### Column Definitions (Base)
| Column | Purpose | Format |
|--------|---------|--------|
| Scene Number | Sequential ID | Integer |
| INT/EXT | Interior/Exterior | Enum or "UNKNOWN" |
| Location | Scene location | Text or "UNKNOWN" |
| Time of Day | DAY/NIGHT/etc | Enum or "UNKNOWN" |
| Story Event | Core action | 1 sentence |
| Subtext | Emotional layer | 5-10 words |
| Turning Point | Type of turn | Action/Revelation/Decision/Realization |
| On Stage | Present characters | Comma-separated |
| Off Stage | Mentioned characters | Comma-separated |
| Character Count | Number present | Integer |
| Protagonist Mood | Emotional state | Predefined options |

### Mode-Specific Extensions
- **Tatort**: +4 columns for investigation tracking
- **Story Beta**: +4 columns for structure + separate Aronson sheet
- **Combined**: Both extensions active

---

## 🎨 UI/UX Principles

### Design System
- **Primary Color**: Indigo-600
- **Background**: White/Gray-50 (Light mode only)
- **Typography**: Inter/System UI
- **Animations**: 300ms ease transitions
- **Responsive**: Mobile-first (< 640px, 640-1024px, > 1024px)

### Step Wizard Flow
1. File validation (format check)
2. Output language selection (DE/EN)
3. Model selection (OpenRouter models)
4. Analysis mode (Standard/Tatort/Story/Combined)
5. Cost estimation & confirmation

### Progress Feedback
- Scene counter: "Analyzing scene X/Y"
- Percentage bar
- Estimated remaining time
- Cancel button (calculates partial costs)

---

## 🚀 API Endpoints

```
POST   /api/v1/upload        # File upload & validation
POST   /api/v1/analyze       # Start analysis
GET    /api/v1/status/{id}   # Status polling
GET    /api/v1/download/{id} # Excel download
DELETE /api/v1/cancel/{id}   # Cancel analysis
```

---

## 🧠 AI Processing Strategy

### Token Optimization
1. **Standard/Tatort modes**:
   - > 15 scenes: Sample 5 start, 5 middle, 5 end
   - ≤ 15 scenes: Analyze all
2. **Story mode**: Always full analysis (structural integrity)
3. **Batch processing**: Group scenes by token count

### Protagonist Detection
Automatic identification based on:
- Desire line clarity
- Goal pursuit consistency
- Story driver role
- Scene presence frequency
- Character arc/transformation

### Error Handling
- Partial failure recovery
- Continue from failure point
- Track and report costs for completed portions

---

## 🔐 Configuration & Security

### Environment Variables
```bash
OPENROUTER_API_KEY=sk-or-v1-xxx  # Required for AI analysis
```

### Limits & Constraints
- Max upload size: 50 MB
- Analysis timeout: 5 minutes
- No logging system (intentional - privacy)
- No data persistence (stateless)

---

## 📝 Development Notes

### Git History Summary
1. Initial setup (v1.0.0)
2. M2 Backend foundation (v1.1)
3. AI analysis integration (v1.2)
4. PDF/FDX parsers (v1.3)
5. Repository reset for fresh start

### Testing Approach
- **Manual testing only** (intentional decision)
- Test files in `examples/` directory
- No automated test suite in MVP

### Known Design Decisions
- ✅ OpenRouter over direct OpenAI
- ✅ All analysis modes from start
- ✅ Light mode only (no dark mode)
- ✅ Docker-first development
- ✅ No statistics in MVP
- ✅ Sequential multi-file processing
- ✅ DE/EN bilingual support
- ❌ No user accounts
- ❌ No data persistence
- ❌ No cloud deployment (local only)

---

## 🔄 Update Protocol

When making structural changes, update this document with:
1. Architecture modifications
2. New dependencies or tools
3. API endpoint changes
4. Processing logic updates
5. UI/UX pattern changes
6. Configuration requirements

**Remember**: This document is for AI agents, not end users. Be technical and precise.

---

## 🎯 Current Status

**Project Phase**: MVP Development
**Next Steps**: 
- Docker setup completion
- Backend API implementation
- Frontend wizard UI
- Integration testing with example files

**Critical Path**:
Docker → Backend Core → AI Integration → Excel Generation → Frontend UI → Testing

---

*End of CLAUDE.md - Version 1.0*