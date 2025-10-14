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
| Backend   | 0%       | -     | ⏳ Pending |
| Frontend  | 0%       | -     | ⏳ Pending |
| **Gesamt** | **0%** | **-** | ⏳ |

---

## Backend-Coverage (Python)

### Module-Level

| Modul | Coverage | Lines | Missed |
|-------|----------|-------|--------|
| `app.parsers` | 0% | 0 | 0 |
| `app.analyzers` | 0% | 0 | 0 |
| `app.api` | 0% | 0 | 0 |
| `app.models` | 0% | 0 | 0 |

### Details

Noch keine Tests vorhanden.

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
