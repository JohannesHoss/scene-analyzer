# Neue Features - 07.11.2025

## 1. Verdächtige/Alibis-Spalte (Nur Crime/Tatort-Modus)

### Was ist das?
Eine neue Spalte die trackt, wer wann verdächtig ist und wer ein Alibi hat.

### Format:
```
Name (Verdächtig - Grund)
Name (Alibi - Details)
Name (Neutral)
Keine Verdächtigen in dieser Szene
```

### Beispiele:

**Szene 5: Erstes Verhör**
```
Jolana (Verdächtig - hatte Zugang zum Schlüssel)
Tanja (Verdächtig - Streit am Vorabend)
Hausmeister (Neutral)
```

**Szene 12: Alibis überprüfen**
```
Jolana (Alibi - war joggen, keine Zeugen)
Andrea (Alibi - war bei Eltern zu Hause)
Stefanie (Verdächtig - war allein, keine Bestätigung)
```

**Szene 35: Geständnis**
```
Jolana (Verdächtig - gesteht den Mord)
Alle anderen (Entlastet)
```

### In der Excel-Tabelle:
Die Spalte heißt:
- Deutsch: **"Verdächtige/Alibis"**
- English: **"Suspects/Alibis"**
- Spaltenbreite: 35 Zeichen
- Position: Nach "Redundanz"

---

## 2. Wendepunkt verfeinert (Alle Modi)

### Was hat sich geändert?
Statt nur einer Spalte "Wendepunkt" gibt es jetzt **zwei Spalten**:

### 2.1. Wendepunkt-Typ
Die Kategorie des Wendepunkts:
- **Action** - Handlung ändert sich
- **Revelation** - Neue Information wird enthüllt
- **Decision** - Charakter trifft Entscheidung
- **Realization** - Charakter erkennt etwas
- **None** - Kein Wendepunkt

### 2.2. Wendepunkt-Moment
Der **genaue Moment/Satz** wo der Wendepunkt passiert.

### Beispiele:

| Szene | Wendepunkt-Typ | Wendepunkt-Moment |
|-------|----------------|-------------------|
| 3 | Revelation | Als Meret die angesägten Karabiner zeigt |
| 15 | Decision | Jolana beschließt, Stefanie zu schützen |
| 22 | Realization | Charlie begreift, dass Stefanie das Opfer war |
| 35 | Revelation | Jolana gesteht den Mord |
| 8 | None | Keiner |

### In der Excel-Tabelle:
- Deutsch: **"Wendepunkt-Typ"** (12 Zeichen) + **"Wendepunkt-Moment"** (40 Zeichen)
- English: **"Turn Type"** (12 Zeichen) + **"Turn Moment"** (40 Zeichen)

---

## Technische Details

### Prompt-Änderungen:

**Deutsch:**
```json
{
  "turning_point_type": "Action|Revelation|Decision|Realization|None",
  "turning_point_moment": "Der genaue Moment/Satz wo der Wendepunkt passiert (z.B. 'Als sie die Tür öffnet und die Leiche sieht') oder 'Keiner'"
}
```

**Crime-Modus zusätzlich:**
```json
{
  "suspect_status": "Liste von Charakteren mit Status: 'Name (Verdächtig - Grund)'|'Name (Alibi - Details)'|'Name (Neutral)' oder 'Keine Verdächtigen in dieser Szene'"
}
```

### Rückwärtskompatibilität:
- Alte Analysen mit `turning_point` werden automatisch zu `turning_point_type` konvertiert
- Falls `turning_point_moment` fehlt, wird "Keiner"/"None" eingesetzt

### Excel-Spalten-Reihenfolge (Crime-Modus):

1. Szene
2. INT/EXT
3. Schauplatz
4. Tageszeit
5. Story Event
6. Subtext
7. **Wendepunkt-Typ** ← NEU: aufgeteilt
8. **Wendepunkt-Moment** ← NEU: aufgeteilt
9. Anwesend
10. Erwähnt
11. Anzahl
12. Stimmung
13. Beweise
14. Info-Fluss
15. Wissensvorsprung
16. Redundanz
17. **Verdächtige/Alibis** ← NEU

---

## Vorteile

### Wendepunkt-Verfeinerung:
✅ Präzisere Szenen-Analyse
✅ Schneller erkennbar WO genau die Wendung stattfindet
✅ Besseres Verständnis der Story-Struktur
✅ Hilfreich für Redakteure beim Überarbeiten

### Verdächtige-Tracking:
✅ Übersicht über Verdachtsentwicklung
✅ Alibi-Tracking auf einen Blick
✅ Hilfreich für Crime-Story-Struktur
✅ Erkennen von Plot-Holes (z.B. vergessene Alibis)

---

## Testing

Teste die neuen Features mit:
```bash
python3 tests/test_tatort_crime.py
```

Die Excel-Datei sollte jetzt enthalten:
- 2 Wendepunkt-Spalten statt 1
- Neue "Verdächtige/Alibis" Spalte im Crime-Modus
