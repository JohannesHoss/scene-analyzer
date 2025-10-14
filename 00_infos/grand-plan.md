---
title: Scene Analyzer - Grand Plan
version: 1.0
date: 14.10.2025
owner: johanneshoss
status: active
depends_on:
  - llm-context.md@1.0
  - architecture.md@1.0
summary: Entwicklungs-Roadmap für Scene Analyzer in 3 Phasen (MVP → Phase 2 → Finalisierung).
---

# Scene Analyzer - Grand Plan v1.0

## 🎯 Gesamt-Vision

Scene Analyzer wird in **3 Phasen** entwickelt:

1. **MVP (v1.0)**: Fountain-Support, Basis-Analyse, CSV-Export
2. **Phase 2 (v2.0)**: Mehr Formate, erweiterte Analyse, Visualisierungen
3. **Finalisierung (v3.0)**: Multi-User, ML-Features, Public API

**Prinzip**: Jede Phase ist vollständig testbar, deploybar und produktiv nutzbar.

---

## 📅 Phase 1: MVP (v1.0)

### Ziel
**Funktionales Minimum**: Upload → Parse → Analyze → Export

### Features
- ✅ Fountain-Format (.fountain) parsen
- ✅ Plain Text mit INT/EXT-Heuristik
- ✅ Basis-Analyse-Parameter:
  - Szenen-Nummer
  - INT/EXT
  - Location
  - Zeit (TAG/NACHT)
  - Charaktere (aus Dialog-Headers)
  - Seitenzahl
  - Geschätzte Länge (Minuten)
- ✅ CSV-Export
- ✅ Single-Session (keine Persistierung)
- ✅ Docker-Setup (dev)

### Tech-Stack MVP
- Backend: FastAPI + fountain-py + pypdf2
- Frontend: Astro + Tailwind + CSV-Download-Button
- Database: Optional PostgreSQL (für Metadaten)
- Deployment: Docker Compose (lokal)

### Milestones

#### M1: Projekt-Setup (2-3 Tage)
- [x] Repo-Struktur (llm-rule konform)
- [x] Git init + main Branch
- [x] Docker Compose (Backend, Frontend, DB)
- [x] Makefile mit `test-report` Target
- [ ] README mit Quick Start
- [ ] CI/CD Basis (GitHub Actions oder GitLab CI)

#### M2: Backend Foundation (5-7 Tage)
- [ ] FastAPI App mit Health-Endpoint
- [ ] Upload-Endpoint (`POST /api/v1/scripts/upload`)
- [ ] Fountain-Parser implementieren
- [ ] Plain Text Parser mit Regex-Heuristik
- [ ] Pydantic Models (Scene, Script, Analysis)
- [ ] Unit-Tests für Parser (Coverage ~70%)
- [ ] Integration-Test: Upload → Parse

#### M3: Analyzer-Logic (3-5 Tage)
- [ ] SceneAnalyzer-Klasse
- [ ] Parameter-Extraktion:
  - INT/EXT aus Header
  - Location aus Header
  - Zeit aus Header
  - Charaktere aus Dialog-Blocks
  - Seitenzahl berechnen
  - Länge schätzen (1 Seite ≈ 1 Min)
- [ ] Analyze-Endpoint (`POST /api/v1/scripts/{id}/analyze`)
- [ ] Unit-Tests für Analyzer
- [ ] Integration-Test: Parse → Analyze

#### M4: Frontend MVP (4-6 Tage)
- [ ] Astro-Projekt init + Tailwind
- [ ] Landing Page (index.astro)
- [ ] Upload-Seite mit Dropzone (React Island)
- [ ] API-Client (fetch wrapper)
- [ ] Analyse-Seite mit Tabelle (TanStack Table)
- [ ] CSV-Export-Button
- [ ] E2E-Test (Playwright): Upload → Analyze → Export

#### M5: Integration & Testing (2-3 Tage)
- [ ] Backend ↔ Frontend Integration
- [ ] Docker Compose vollständig
- [ ] Smoke-Tests: Happy Path durchgängig
- [ ] Test-Reports in `89_output/test_reports/`
- [ ] Reports aktualisieren (`90_reports/`)
- [ ] Coverage-Check (~60%)

#### M6: MVP-Release (1-2 Tage)
- [ ] Deployment-Dokumentation
- [ ] User-Guide (README)
- [ ] Version-Bump auf v1.0
- [ ] Git-Tag: `v1.0.0`
- [ ] Optional: Erster Deployment auf Test-Server

**Timeline MVP**: ~17-26 Tage (3-4 Wochen)

---

## 📅 Phase 2: Erweiterte Features (v2.0)

### Ziel
**Mehr Formate, bessere Analyse, Visualisierungen**

### Features
- ✅ PDF-Support (pypdf2 + Layout-Heuristik)
- ✅ Final Draft FDX (XML-Parsing)
- ✅ Erweiterte Parameter:
  - Dialog-Anteil (% Dialog vs. Action)
  - Action-Lines-Count
  - Emotionaler Ton (Heuristik)
  - Requisiten/Props (Keyword-Extraction)
- ✅ Excel-Export (openpyxl, formatierte Tabellen)
- ✅ JSON-Export
- ✅ Visualisierungen:
  - Timeline (Szenen-Abfolge)
  - Charakter-Frequenz (Balkendiagramm)
  - INT/EXT-Verteilung (Pie Chart)
- ✅ Persistierung: Analysen speichern (PostgreSQL)
- ✅ Optional: Async Job Queue (Celery + Redis für große PDFs)

### Tech-Erweiterungen
- Backend: + Celery, openpyxl, beautifulsoup4
- Frontend: + Chart.js, React Components für Charts
- Database: PostgreSQL zwingend

### Milestones

#### M7: PDF & FDX Parser (5-7 Tage)
- [ ] PDF-Parser (pypdf2, Text-Extraktion)
- [ ] FDX-Parser (XML-Parsing mit lxml)
- [ ] Format-Detection verbessern
- [ ] Tests für neue Parser

#### M8: Erweiterte Analyse (4-6 Tage)
- [ ] Dialog vs. Action Berechnung
- [ ] Ton-Heuristik (Keywords: "schießt", "lacht", etc.)
- [ ] Props-Extraktion (Regex + Dictionary)
- [ ] Tests für erweiterte Parameter

#### M9: Export-Optionen (3-4 Tage)
- [ ] Excel-Export mit Formatierung
- [ ] JSON-Export
- [ ] Export-Endpoint erweitern
- [ ] Tests für Exports

#### M10: Visualisierungen (5-7 Tage)
- [ ] Chart.js Integration
- [ ] Timeline-Component (React)
- [ ] Charakter-Frequenz-Chart
- [ ] INT/EXT Pie Chart
- [ ] Responsive Design

#### M11: Persistierung (3-5 Tage)
- [ ] PostgreSQL-Schema erweitern (Analyses-Tabelle)
- [ ] CRUD für Analysen
- [ ] GET /api/v1/analyses/{id}
- [ ] Liste aller Analysen (optional)
- [ ] Tests für DB-Layer

#### M12: Phase 2 Release (2-3 Tage)
- [ ] Integration-Tests für neue Features
- [ ] Dokumentation aktualisieren
- [ ] Version-Bump auf v2.0
- [ ] Git-Tag: `v2.0.0`
- [ ] Deployment auf Prod-Server

**Timeline Phase 2**: ~22-32 Tage (4-5 Wochen)

---

## 📅 Phase 3: Finalisierung (v3.0)

### Ziel
**Multi-User, ML, Public API**

### Features
- ✅ User Accounts (OAuth: Google, GitHub)
- ✅ Projekt-Management (Drehbücher speichern, teilen)
- ✅ Word-Support (DOCX-Parsing)
- ✅ ML-Features:
  - Sentiment-Analyse (spacy oder transformers)
  - Charakter-Arc-Tracking
  - Automatische Genre-Erkennung
- ✅ Public REST API (mit API-Keys)
- ✅ Kosten-Schätzung (Budget-Kategorien)
- ✅ Produktions-Komplexität (Scoring)
- ✅ Webhooks (optional, für Integrationen)
- ✅ DSGVO-Compliance (Daten-Export, Löschung)

### Tech-Erweiterungen
- Backend: + spacy, transformers, Auth-Library
- Frontend: + User-Dashboard, Project-Management-UI
- Infrastructure: + S3/MinIO für File-Storage

### Milestones

#### M13: Auth & User-Management (7-10 Tage)
- [ ] OAuth2 Integration (Google, GitHub)
- [ ] JWT-Token-Handling
- [ ] User-Model + DB-Schema
- [ ] Login/Logout-Flow
- [ ] Tests für Auth

#### M14: Project-Management (5-7 Tage)
- [ ] Projects-Tabelle (DB)
- [ ] CRUD-Endpoints für Projects
- [ ] Frontend: Dashboard, Project-Liste
- [ ] Teilen-Funktion (optional)

#### M15: DOCX-Support (3-4 Tage)
- [ ] DOCX-Parser (python-docx)
- [ ] Tests für DOCX

#### M16: ML-Features (10-14 Tage)
- [ ] spacy-Modell integrieren (de_core_news_md)
- [ ] Sentiment-Analyse pro Szene
- [ ] Charakter-Arc (Szenen-übergreifend)
- [ ] Genre-Heuristik (Keywords + ML)
- [ ] Tests für ML-Pipeline

#### M17: Public API (5-7 Tage)
- [ ] API-Key-Generation
- [ ] Rate-Limiting (erweitert)
- [ ] API-Dokumentation (OpenAPI/Swagger)
- [ ] Webhook-Support (optional)

#### M18: Kosten & Komplexität (4-6 Tage)
- [ ] Budget-Scoring (Heuristik: Location, SFX, etc.)
- [ ] Produktions-Komplexität (1-10 Skala)
- [ ] UI für Scoring

#### M19: DSGVO & Security (3-5 Tage)
- [ ] Daten-Export (GDPR)
- [ ] Lösch-Funktion
- [ ] Privacy-Policy
- [ ] Security-Audit

#### M20: Final Release (3-5 Tage)
- [ ] Full Integration-Tests
- [ ] Performance-Tests (Load-Testing)
- [ ] Dokumentation finalisieren
- [ ] Version-Bump auf v3.0
- [ ] Git-Tag: `v3.0.0`
- [ ] Prod-Deployment

**Timeline Phase 3**: ~40-58 Tage (6-9 Wochen)

---

## 📊 Gesamt-Timeline

| Phase | Dauer | Kumulativ |
|-------|-------|-----------|
| MVP (v1.0) | 3-4 Wochen | 3-4 Wochen |
| Phase 2 (v2.0) | 4-5 Wochen | 7-9 Wochen |
| Phase 3 (v3.0) | 6-9 Wochen | 13-18 Wochen |

**Total**: ~3-4.5 Monate (bei Vollzeit-Entwicklung)

---

## 🚦 Decision Gates

Zwischen Phasen: **Go/No-Go-Entscheidung**

### Gate 1 (nach MVP)
- ✅ Alle MVP-Features funktionieren
- ✅ Tests grün (Coverage ~60%)
- ✅ Docker-Deployment läuft
- ✅ User-Feedback eingeholt

**Kriterien für Phase 2**:
- MVP wird aktiv genutzt (min. 10 User)
- Feedback positiv (NPS > 7)
- Budget für Phase 2 vorhanden

### Gate 2 (nach Phase 2)
- ✅ Erweiterte Features stabil
- ✅ Performance ok (<2s für Analyse)
- ✅ User-Feedback für Multi-User-Bedarf

**Kriterien für Phase 3**:
- Kommerzielle Nutzung geplant
- Budget für ML + Infra-Scaling
- Legal-Clearing (DSGVO) durchgeführt

---

## 🔄 Iterativer Prozess

Jede Phase folgt:
1. **Design**: Architektur-Entscheidungen dokumentieren
2. **Implement**: Coding + Tests
3. **Test**: Unit + Integration + E2E
4. **Report**: `90_reports/` aktualisieren
5. **Deploy**: Docker-Image bauen + pushen
6. **Review**: Feedback einholen, Learnings dokumentieren

---

## 🎯 Erfolgskriterien

### MVP
- [ ] User kann Fountain-Drehbuch hochladen
- [ ] Szenen werden korrekt erkannt (>90% Accuracy)
- [ ] CSV-Export funktioniert
- [ ] Deployment auf Test-Server läuft

### Phase 2
- [ ] PDF + FDX werden korrekt geparst
- [ ] Visualisierungen sind interaktiv
- [ ] Performance: <5s für 100-Seiten-PDF

### Phase 3
- [ ] Multi-User funktioniert ohne Konflikte
- [ ] ML-Features liefern plausible Ergebnisse
- [ ] Public API wird von min. 5 Dritt-Tools genutzt

---

## 🛑 Risiken & Mitigations

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| PDF-Parsing fehleranfällig | Hoch | Mittel | Fallback auf Plain Text Heuristik |
| ML-Modelle zu langsam | Mittel | Hoch | Async Job Queue (Celery) |
| DSGVO-Compliance komplex | Mittel | Hoch | Frühzeitig Legal-Experten einbinden |
| User-Adoption niedrig | Mittel | Mittel | Early-Access-Programm, Feedback-Loops |

---

## 📚 Dependencies (External)

- **Fountain-Spec**: https://fountain.io
- **FastAPI**: https://fastapi.tiangolo.com
- **Astro**: https://astro.build
- **spacy**: https://spacy.io
- **TanStack Table**: https://tanstack.com/table

---

**Version**: 1.0  
**Letztes Update**: 14.10.2025  
**Nächstes Review**: Nach M6 (MVP-Release)
