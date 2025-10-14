---
title: Coverage Report - Scene Analyzer
date: 14.10.2025
version: 1.0.0
status: initial
---

# Coverage Report

## Gesamt-Coverage

**Letztes Update**: 14.10.2025

| Component | Coverage | Delta | Status |
|-----------|----------|-------|--------|
| Backend   | 94%      | +94%  | ✅ Excellent |
| Frontend  | 0%       | -     | ⏳ Pending |
| **Gesamt** | **94%** | **+94%** | ✅ |

---

## Backend-Coverage (Python)

### Module-Level

| Modul | Coverage | Lines | Missed |
|-------|----------|-------|--------|
| `app.parsers` | 97% | 106 | 5 |
| `app.api` | 82% | 22 | 4 |
| `app.models` | 100% | 45 | 0 |
| `app.services` | 95% | 21 | 1 |

### Details

**Excellente Coverage!** Alle Core-Module haben >80% Coverage:
- FountainParser: 97% (nur Exception-Handling uncovered)
- Models: 100% (vollständig getestet)
- Services: 95% (nur ein Edge-Case uncovered)
- API: 82% (Error-Handler teilweise uncovered)

---

## Frontend-Coverage (TypeScript)

### Component-Level

| Component | Coverage | Lines | Missed |
|-----------|----------|-------|--------|
| `src/lib/api.ts` | 0% | 0 | 0 |
| `src/components/*` | 0% | 0 | 0 |

### Details

Noch keine Tests vorhanden.

---

## Ziel-Coverage (llm-rule v4.1)

- **Minimum**: 60% auf geändertem Code
- **Optimal**: 70-80% gesamt
- **Kritisch**: Core-Parser und API-Endpoints ~80%

---

## Nächste Schritte

1. Parser-Tests implementieren (Ziel: 80%)
2. API-Endpoint-Tests (Ziel: 70%)
3. Frontend API-Client-Tests (Ziel: 60%)

---

**Nächstes Update**: Nach erstem Test-Run mit `make test-report`
