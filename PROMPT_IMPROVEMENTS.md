# Prompt Verbesserungen

## Änderungen vom 07.11.2025

### 1. Schauplatz & Tageszeit aus Kontext

**Vorher:** Wurden nur per Regex aus dem Text erkannt (funktionierte schlecht bei Treatments)

**Jetzt:** AI extrahiert aus dem Kontext:
```json
{
  "location": "Konkreter Schauplatz aus dem Text (z.B. 'Wohnzimmer', 'Polizeirevier', 'Park')",
  "time_of_day": "Tageszeit aus dem Kontext (z.B. 'Morgen', 'Nachmittag', 'Nacht', 'Unbekannt')",
  "int_ext": "INT|EXT|UNBEKANNT (Innenraum oder Außenbereich)"
}
```

### 2. Wendepunkt - Klarere Definitionen

**Vorher:** `"turning_point": "Action|Revelation|Decision|Realization|None"`

**Jetzt mit Erklärungen:**
```
"turning_point": "Action (Handlung ändert sich)|Revelation (neue Info)|Decision (Entscheidung)|Realization (Erkenntnis)|None"
```

**Was ist ein Wendepunkt?**
- **Action**: Die Handlung nimmt eine neue Richtung (z.B. plötzlicher Angriff)
- **Revelation**: Neue Information wird enthüllt (z.B. Geständnis)
- **Decision**: Charakter trifft wichtige Entscheidung (z.B. beschließt zu fliehen)
- **Realization**: Charakter erkennt etwas (z.B. begreift den Verrat)
- **None**: Szene ist Status Quo, keine Wendung

### 3. Wissensvorsprung (Knowledge Gap) - Klarere Formulierung

**Vorher:** `"knowledge_gap": "Viewer>Character|Character>Viewer|Equal"`

**Jetzt:**
```
"knowledge_gap": "Zuschauer weiß mehr als Figur|Figur weiß mehr als Zuschauer|Beide wissen gleich viel"
```

**Beispiele:**
- **Zuschauer > Figur**: Wir sehen, wie jemand Gift ins Glas schüttet, aber die Figur weiß es nicht
- **Figur > Zuschauer**: Der Detektiv hat einen Verdacht, aber wir wissen nicht warum
- **Gleichstand**: Beide erfahren gleichzeitig die Information

### 4. Redundanz - Mit Erklärungen

**Vorher:** `"redundancy": "New info|Repetition|Variation"`

**Jetzt:**
```
"redundancy": "Neue Info (erste Erwähnung)|Wiederholung (exakt gleich)|Variation (neue Perspektive auf bekannte Info)"
```

**Beispiele:**
- **Neue Info**: Zum ersten Mal wird erwähnt, dass der Täter hinkt
- **Wiederholung**: Zeuge wiederholt exakt das gleiche wie vorher
- **Variation**: Wir hören die gleiche Geschichte, aber aus anderer Perspektive mit neuen Details

### 5. Informationsfluss - Detaillierte Kategorien

**Jetzt mit Erklärungen:**
```
"information_flow": "Wahrheit (sagt die Wahrheit)|Lüge (lügt aktiv)|Teilgeständnis (halb wahr)|Verschweigen (lässt Info weg)|Irreführung (lenkt ab)"
```

### 6. Stimmung (Protagonist Mood) - Erweitert

**Jetzt mit "Neutral" als Option:**
```
"protagonist_mood": "Wütend|Verzweifelt|Hoffnungsvoll|Erschöpft|Triumphierend|Verwirrt|Entschlossen|Neutral"
```

## Technische Änderungen

### AI-Werte überschreiben Regex-Werte
```python
result = {
    "int_ext": analysis.get("int_ext", scene.get("int_ext", "UNKNOWN")),
    "location": analysis.get("location", scene.get("location", "UNKNOWN")),
    "time_of_day": analysis.get("time_of_day", scene.get("time_of_day", "UNKNOWN")),
}
```

Fallback-Logik:
1. Versuche AI-Wert zu verwenden
2. Falls nicht vorhanden: Nutze Regex-Wert
3. Falls auch nicht vorhanden: "UNKNOWN"

## Testing

Nach diesen Änderungen sollte die Analyse:
- ✅ Schauplätze aus dem Kontext korrekt erkennen
- ✅ Tageszeiten verstehen (auch implizite wie "Sonnenaufgang")
- ✅ Wendepunkte präziser kategorisieren
- ✅ Wissensvorsprung klarer identifizieren
- ✅ Redundanz-Level besser einschätzen
