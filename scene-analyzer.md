# Scene Analyzer - Drehbuch-Analyse Tool

## 🎯 Übersicht

**Vollautomatisches Analyse-Tool für Drehbücher und Treatments**
- Uploadet ein Drehbuch/Treatment → Erhalte detaillierte Excel-Analyse
- Unterstützt Deutsch & Englisch (Input automatisch erkannt, Output vom User gewählt)
- Läuft lokal mit Docker auf Mac/Windows/Linux

## 🎨 Frontend-Design-Specs

### UI-Komponenten:
- **Upload-Area**: Dezenter Drag&Drop-Bereich, zeigt Dateinamen nach Upload
- **Step-Wizard**: 5 Schritte mit Progress-Indicator oben
- **Kosten-Widget**: Floating Badge rechts oben (einfacher Light Mode Stil)
- **Progress-Modal**: Zentriert mit einfachem Light Mode Background
- **Error-Modal**: Mit Retry/Cancel Buttons
- **Language Toggle**: Top-Right Corner (DE/EN)

### Design-System:
- **Primary Color**: Indigo-600 (buttons, progress)
- **Background**: Light (white/gray-50)
- **Cards**: White with shadow
- **Text**: Gray-900 primary, Gray-600 secondary
- **Animations**: Smooth transitions (300ms ease)
- **Font**: Inter/System UI

### Responsive Breakpoints:
- Mobile: < 640px (single column)
- Tablet: 640px - 1024px 
- Desktop: > 1024px (centered container max-w-6xl)

## 📁 Projekt-Struktur

```
scene-analyzer/
├── docker-compose.yml     # Container-Orchestrierung
├── .env                   # API Keys (nicht in Git!)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py        # FastAPI App
│       ├── parsers/       # PDF/DOCX/TXT Parser
│       ├── analyzer/      # KI-Analyse Logik
│       └── excel/         # Excel-Generator
├── frontend/
│   ├── Dockerfile
│   └── static/
│       ├── index.html     # Upload UI
│       ├── app.js         # Upload Logic
│       └── styles.css     # (Optional, nutzen Tailwind CDN)
├── examples/              # Beispiel-Drehbücher (nur Ordner, keine Beispieldateien)
│   ├── screenplays/       # Drehbücher (alle Sprachen)
│   └── treatments/        # Treatments (alle Sprachen)
```

## 🛠️ API Endpoints

```
POST   /api/v1/upload        # Datei hochladen & validieren
POST   /api/v1/analyze       # Analyse starten
GET    /api/v1/status/{id}   # Status abfragen (Polling)
GET    /api/v1/download/{id} # Excel downloaden
DELETE /api/v1/cancel/{id}   # Analyse abbrechen
```

## 📊 Logging-Strategie

- **Kein Logging-System** im MVP (bewusste Entscheidung)

## 🏗️ Tech-Stack (Finalisiert)

### Backend Container
- **Python 3.12+** mit **FastAPI**
- **Port**: 8001 (um Kollisionen zu vermeiden)
- **Libraries**:
  - `pypdf2` - PDF parsing
  - `python-docx` - DOCX parsing  
  - `requests` - HTTP Client für OpenRouter API
  - `openpyxl` - Excel generation
  - `pydantic` - Type validation
  - `python-multipart` - File uploads
- **OpenRouter API Key**: Via `.env` file

### Frontend Container  
- **Nginx** - Static file server
- **Port**: 3000 (um Kollisionen zu vermeiden)
- **Tailwind CSS** (via CDN) - Styling
- **Vanilla JavaScript** - File upload & API calls
- **No build process** - Pure HTML/CSS/JS

### Infrastructure
- **Docker Compose** - 2 Container Setup
- **Keine Datenbank** - Alles in-memory (bis Download abgeschlossen)
- **Volumes**: None (stateless)
- **Networks**: Internal bridge network

### Development & Deployment
- **Entwicklung**: Docker Desktop auf Mac (localhost)
- **Deployment**: Nur lokal (Option A)
- **Zugriff**: http://localhost:3000
- **Production**: Später möglich auf jedem Docker Host
- **CORS**: Nicht benötigt (Docker-interne Kommunikation)

## 🔧 Konfiguration

### OpenRouter Integration
- **API Key**: Wird über .env bereitgestellt
- **Modell-Auswahl**: User kann im Frontend zwischen verfügbaren Modellen wählen
- **Verfügbare Modelle**:
  - OpenAI GPT-4o-mini (Default - schnell & günstig)
  - OpenAI GPT-4o (volle Leistung, teurer)
  - Claude 3 Haiku (sehr schnell, sehr günstig)
  - Gemini 1.5 Flash (Google, günstig)
  - Llama 3.1 70B (Open Source Alternative)
- **Modell-Dropdown**: Im Step-Wizard nach Sprach-Auswahl

### Limits & Settings
- **Max Upload Size**: 50 MB
- **Analyse Timeout**: 5 Minuten
- **Error Handling**: Klare Fehlermeldungen anzeigen
- **Sprachen**: Input-Sprache automatisch erkannt, Output-Sprache User-Auswahl

---

## 🎯 Projekt-Ziel

**Vollautomatisches Drehbuch-Analyse-Tool**
- Input: PDF, DOCX, TXT (Drehbücher & Treatments)
- Output: Excel-Tabelle mit detaillierter Szenenanalyse
- Sprachen: Deutsch & Englisch (automatische Erkennung)

## 📊 Output-Tabellen-Struktur

### Englische Version (Basis):
| Scene Number | INT/EXT | Location | Time of Day | Story Event | Subtext | Turning Point | On Stage | Off Stage | Character Count | Protagonist Mood |

### Deutsche Version (Basis):
| Szenennummer | INT/EXT | Schauplatz | Tageszeit | Story Event | Subtext | Wendepunkt | Anwesend | Erwähnt | Anzahl | Stimmung Protagonist |

### Tatort-Modus (zusätzliche Spalten):
| Evidence | Information Flow | Knowledge Gap | Redundancy Check |

### Story-Modus Beta:

#### Sheet 1 - Szenen-Analyse (zusätzliche Spalten):
| Hero's Journey | Act | Plot Point (Actual) | Plot Point (Expected) |

#### Sheet 2 - Aronson Single Path Analyse (separates Blatt):
Gesamtanalyse des Drehbuchs nach Linda Aronsons Methode

### Spalten-Definitionen (Basis-Analyse):
- **Scene Number**: Fortlaufende Nummerierung
- **INT/EXT**: Interior/Exterior oder INNEN/AUSSEN (bei Unklarheit: "UNKNOWN")
- **Location**: Drehort (z.B. "KITCHEN" oder "KÜCHE", bei Unklarheit: "UNKNOWN")
- **Time of Day**: DAY/NIGHT/DAWN/DUSK etc. (bei Unklarheit: "UNKNOWN")
- **Story Event**: Prägnante Zusammenfassung (1 Satz)
- **Subtext**: Emotionale/unterschwellige Ebene (5-10 Wörter)
- **Turning Point**: Action/Revelation/Decision/Realization
- **On Stage**: Alle anwesenden Personen (sprechend + stumm)
- **Off Stage**: Erwähnte aber nicht anwesende Personen
- **Character Count**: Anzahl der On-Stage Personen
- **Protagonist Mood** / **Stimmung Protagonist**: Wütend/Verzweifelt/Hoffnungsvoll/Erschöpft/Triumphierend/Verwirrt/Entschlossen

### Zusätzliche Spalten (Tatort-Modus):
Wenn "Tatort-Modus" gewählt wird, kommen diese Spalten dazu:
- **Beweismittel**: Physische Spuren und Objekte die gefunden/übersehen werden
- **Informationsfluss**: Wahrheit/Lüge/Teilgeständnis/Verschweigen/Irreführung
- **Wissensvorsprung**: "Zuschauer > Figur" / "Figur > Zuschauer" / "Gleichstand"
- **Redundanz-Check**: Neue Info/Wiederholung/Variation

### Story-Modus Beta Details:

#### Sheet 1 - Zusätzliche Spalten in Haupttabelle:
Wenn "Story-Modus (Beta)" gewählt wird, kommen diese Spalten dazu:
- **Hero's Journey Stage**: Ordinary World / Call to Adventure / Crossing Threshold / Tests & Allies / Approach / Ordeal / Reward / Road Back / Resurrection / Return with Elixir / Not Applicable
- **Act Structure**: Act I (Setup) / Act II-A (Rising Action) / Act II-B (Complications) / Act III (Resolution)
- **Plot Point Actual**: Tatsächlicher Wendepunkt falls vorhanden (Inciting Incident / Plot Point 1 / Midpoint / Plot Point 2 / Climax / Resolution / None)
- **Plot Point Expected**: Wo sollte ein Wendepunkt sein basierend auf Position (z.B. "Plot Point 1 expected here (25%)")

#### Sheet 2 - Aronson Analyse (separates Excel-Blatt):
Strukturanalyse nach Linda Aronson - User wird im Story-Modus gefragt ob mehrere Hauptfiguren analysiert werden sollen:

**Single Path / Multiple Path Analyse:**

| Frage (DE) | Frage (EN) | Antwort |
|------------|------------|----------|
| **1. Wer ist die Hauptfigur, und was will sie unbedingt?** | Who is the protagonist and what do they absolutely want? | [Analyse] |
| **2. Welche Hindernisse stehen ihr im Weg?** | What obstacles stand in their way? | [Analyse] |
| **3. Was ist der Inciting Incident (auslösendes Ereignis)?** | What is the inciting incident? | [Analyse] |
| **4. Wie verschärfen sich die Konflikte im Mittelteil?** | How do conflicts intensify in the middle? | [Analyse] |
| **5. Was ist der Climax – der Moment der Entscheidung?** | What is the climax - the moment of decision? | [Analyse] |
| **6. Wie verändert sich die Figur bis zum Ende?** | How does the character change by the end? | [Analyse] |
| **7. Gibt es eine durchgehende Action Line?** | Is there a continuous action line? | [Analyse] |
| **8. Gibt es eine parallele Relationship Line?** | Is there a parallel relationship line? | [Analyse] |
| **9. Wie ist die Balance zwischen Inner/Outer Story?** | What's the balance between inner/outer story? | [Analyse] |
| **10. Hat der Protagonist einen erkennbaren Makel (Flaw)?** | Does the protagonist have a recognizable flaw? | [Analyse] |

**Bei Multiple Path: Wiederholung der kompletten Tabelle für jede Hauptfigur untereinander**

### Szenen-Erkennung bei Treatments (ohne klare Sluglines):
1. **Primär**: Sluglines (INT./EXT.)
2. **Zeitsprünge**: "Später", "Am nächsten Tag" → neue Szene
3. **Locationwechsel**: "Währenddessen im...", "In der Küche" → neue Szene
4. **Doppelte Leerzeile**: Möglicher Szenenwechsel
5. **Fallback**: Nach ~300-500 Wörtern automatisch teilen

### Excel-Statistiken:
- **Keine Statistiken im MVP** (auf Benutzerwunsch entfernt)

## 🔄 Workflow

```
1. User lädt Datei(en) hoch (Drag & Drop oder Button)
   ↓
2. Step-by-Step Wizard:
   - Step 1: Datei-Validierung (Format-Check)
   - Step 2: Ausgabesprache wählen (DE/EN)
   - Step 3: Modell auswählen (Dropdown mit OpenRouter Modellen)
   - Step 4: Analyse-Modus (Standard / Tatort / Story-Beta / Tatort+Story-Beta)
   - Step 4a: Bei Story-Modus: Anzahl Hauptfiguren für Aronson-Analyse wählen
   - Step 5: Kosten-Schätzung bestätigen
   ↓
3. Analyse startet:
   - Progress Bar + "Analysiere Szene X/Y"
   - Geschätzte Restzeit (basierend auf Durchschnittszeit pro Szene)
   - Cancel-Button (bricht ab, berechnet bisherige Kosten)
   ↓
4. System erkennt Format (Drehbuch/Treatment/Mixed - wenn beide Formate gemischt)
   ↓
5. Parser extrahiert Szenen
   ↓
6. Gewähltes Modell analysiert:
   - Story Event
   - Subtext  
   - Turning Points
   - Charaktere
   - Protagonist (automatisch erkannt basierend auf Story-Struktur-Kriterien)
   - Stimmung Protagonist
   ↓
7. Excel-Generation mit Formatierung
   ↓
8. "Download bereit" Button + Kosten-Anzeige (Tatsächlich: X.XX€)
   - Dateiname: `{original_filename}_analyse_{datum}.xlsx`
   - Bei Multi-File: Separate Downloads nacheinander
```

## 🤖 KI-Integration

- **Modell**: Start mit GPT-4o-mini über OpenRouter (weitere Modelle verfügbar)
- **Kosten**: Variable je nach gewähltem Modell (Token-Zählung während Analyse)
- **Kosten-Anzeige**: Vor und nach der Analyse
- **Rate Limiting**: Abhängig von OpenRouter Limits
- **Analyse-Strategie**:
  1. Bei Standard/Tatort-Modi: 
     - Bei >15 Szenen: 5 vom Anfang, 5 aus der Mitte, 5 vom Ende (Kosten sparen)
     - Bei ≤15 Szenen: Alle Szenen analysieren
  2. Bei Story-Modus: Komplette Analyse aller Szenen (für vollständige Struktur-Analyse)
  3. Batch-Processing (optimiert nach Token-Count)
  4. Bei Story-Modus (Beta): Zweite Analyse-Phase für Gesamtstruktur:
     - Hero's Journey & Plot Points pro Szene
     - Separates Sheet: Aronson Analyse (10 Kernfragen, bei Multiple Path für jede Hauptfigur)
- **Fehlerbehandlung**: Bei Teilausfall automatisch ab Fehlerstelle fortsetzen

## 🏗️ Implementierungs-Phasen

### ✅ Entscheidungen vom User:
1. ✅ OpenRouter statt OpenAI (mit o1-mini als Start)
2. ✅ Alle Modi implementieren (Standard, Tatort, Story-Beta)
3. ✅ Light Mode UI (kein Dark Mode)
4. ✅ Docker Setup wie geplant
5. ✅ Gruppierte Spalten nur für Modi, keine Statistiken
6. ✅ Multi-File sequenziell verarbeiten
7. ✅ DE/EN Sprach-Features beibehalten
8. ✅ Modell-Auswahl im Frontend (Dropdown)
9. ✅ Nur examples Ordner erstellen (keine komplette Struktur vorab)
10. ✅ Standard-Entwicklungsreihenfolge: Docker → Backend → Frontend

### Phase 1: Docker Setup & Backend Core (Tag 1-2)
- [ ] Docker Compose mit 2 Containern
- [ ] FastAPI Grundgerüst
- [ ] File Upload Endpoint
- [ ] PDF/DOCX/TXT Parser
- [ ] Szenen-Extraktion Logik
- [ ] Sprach-Erkennung (DE/EN)

### Phase 2: KI-Integration (Tag 3-4)
- [ ] OpenRouter Client Setup
- [ ] Prompt-Templates für Story Event
- [ ] Subtext & Turning Point Analyse
- [ ] Charakter-Extraktion
- [ ] Batch-Processing (Token-optimiert)
- [ ] Error Handling & Retries

### Phase 3: Excel-Generation (Tag 5)
- [ ] Multi-Language Headers (DE/EN)
- [ ] Formatierung & Styling:
  - Auto-Width für alle Spalten
  - Header: Fett, Hintergrundfarbe
  - Gruppierte Spalten nur für Modi (Tatort/Story)
- [ ] Download Response Headers

### Phase 4: Frontend UI (Tag 6-7)
- [ ] Nginx Container Setup
- [ ] HTML mit Tailwind CSS
- [ ] Vanilla JS für Wizard-Interaktivität
- [ ] Step-by-Step Upload Wizard
- [ ] Drag & Drop Upload (zeigt Dateinamen dezent)
- [ ] Progress Bar mit Szenen-Counter + Restzeit + Cancel
- [ ] Error Modal mit Retry-Button
- [ ] Responsive Design (Mobile-First)
- [ ] Language Toggle (DE/EN)
- [ ] Multi-File Upload Support (sequenziell verarbeitet)

## 🎯 MVP-Features

✅ **Enthalten:**
- Voll-automatische Analyse mit minimaler User-Interaktion
- PDF, DOCX, TXT Support (50 MB max)
- Deutsch/Englisch Ausgabesprache (User-Auswahl)
- Excel-Export mit Basis-Formatierung (gruppierte Spalten nur für Modi)
- Bei Story-Modus: 2 Sheets (Szenen + Aronson Analyse)
- Story Grid inspirierte Analyse
- Tatort-Modus (optional)
- Story-Modus für Strukturanalyse (Beta)
- Kombinierbar: Tatort + Story gleichzeitig
- UI mit Tailwind CSS (Light Mode)
- Progress-Anzeige: Szenen-Counter + Prozentbalken + Restzeit
- Kosten-Transparenz (Schätzung vorher, tatsächlich nachher)
- **Automatische Protagonist-Erkennung** (basierend auf: Desire Line, Goal-Verfolgung, Story-Treiber, Szenen-Präsenz, Veränderungsbogen)
- Multi-File Processing (sequenziell)
- UI Language Toggle (DE/EN)
- Mobile-First Responsive Design

❌ **Nicht im MVP:**
- User Accounts / Login
- Manuelle Bearbeitung der Ergebnisse
- Multiple Export-Formate
- Datenbank / Historie
- Cloud Deployment
- API für Drittanbieter

## 🧪 Testing-Strategie

- **Manuelles Testing** mit echten Drehbüchern
- **Keine automatisierten Tests** (bewusste Entscheidung)
- **Direktes Testing** während der Entwicklung
- **User hat bereits Test-Drehbücher** zum Ausprobieren

## 🚀 Quick Start

```bash
# 1. Repository klonen
# Lokale Entwicklung - noch kein Git Repo
cd scene-analyzer

# 2. OpenRouter API Key setzen
echo "OPENROUTER_API_KEY=dein-key-hier" > .env

# 3. Docker Container starten
docker-compose up

# 4. Browser öffnen
open http://localhost:3000

# 5. Drehbuch hochladen & Excel erhalten!
```
