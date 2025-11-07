#!/usr/bin/env python3
"""Test script to demonstrate Aronson analysis Excel output"""

import sys
sys.path.insert(0, '/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/backend/app')

from excel.generator import ExcelGenerator
from analyzer.scene_analyzer import ARONSON_QUESTIONS_DE, ARONSON_QUESTIONS_EN

# Mock analysis data (minimal for demo)
mock_scenes = [
    {
        "number": 1,
        "int_ext": "INT",
        "location": "WOHNZIMMER",
        "time_of_day": "NACHT",
        "story_event": "Anna findet einen mysteriösen Brief",
        "subtext": "Angst und Neugier kämpfen",
        "turning_point_type": "Revelation",
        "turning_point_moment": "Als sie den Brief öffnet",
        "on_stage": ["Anna", "Max"],
        "off_stage": ["Peter"],
        "protagonist_mood": "Verwirrt",
        "hero_journey": "Call to Adventure",
        "act": "Act I",
        "plot_point_actual": "Inciting Incident",
        "plot_point_expected": "Inciting Incident expected here (10%)"
    },
    {
        "number": 2,
        "int_ext": "EXT",
        "location": "PARK",
        "time_of_day": "TAG",
        "story_event": "Anna trifft den geheimnisvollen Fremden",
        "subtext": "Vertrauen wird auf die Probe gestellt",
        "turning_point_type": "Decision",
        "turning_point_moment": "Sie entscheidet sich ihm zu folgen",
        "on_stage": ["Anna", "Fremder"],
        "off_stage": [],
        "protagonist_mood": "Entschlossen",
        "hero_journey": "Crossing Threshold",
        "act": "Act I",
        "plot_point_actual": "None",
        "plot_point_expected": "Building to Plot Point 1"
    }
]

# Mock Aronson answers in German
mock_aronson_de = [
    {
        "question": ARONSON_QUESTIONS_DE[0],
        "answer": "Die Hauptfigur ist Anna, eine 32-jährige Journalistin, die unbedingt die Wahrheit über das Verschwinden ihrer Schwester herausfinden will. Ihre Motivation wird durch Schuldgefühle und den Wunsch nach Wiedergutmachung angetrieben."
    },
    {
        "question": ARONSON_QUESTIONS_DE[1],
        "answer": "Ihr stehen mehrere Hindernisse im Weg: die Polizei glaubt ihr nicht, ihr Chef droht mit Kündigung, und der mysteriöse Fremde scheint mehr zu wissen als er preisgibt. Zudem kämpft sie mit ihren eigenen Zweifeln und Ängsten."
    },
    {
        "question": ARONSON_QUESTIONS_DE[2],
        "answer": "Der Inciting Incident ist der mysteriöse Brief, den Anna in Szene 1 erhält. Er enthält einen Hinweis auf den Aufenthaltsort ihrer verschwundenen Schwester und zwingt Anna dazu, ihre sichere Welt zu verlassen und aktiv zu werden."
    },
    {
        "question": ARONSON_QUESTIONS_DE[3],
        "answer": "Die Konflikte verschärfen sich durch zunehmende Bedrohungen: Anna wird verfolgt, erhält Drohbriefe, und Menschen in ihrem Umfeld beginnen sich seltsam zu verhalten. Jede Antwort führt zu drei neuen Fragen."
    },
    {
        "question": ARONSON_QUESTIONS_DE[4],
        "answer": "Der Climax ist der Moment, in dem Anna ihrer Schwester gegenübersteht und erkennt, dass diese freiwillig verschwunden ist. Anna muss entscheiden, ob sie die Wahrheit veröffentlicht oder ihre Schwester schützt."
    },
    {
        "question": ARONSON_QUESTIONS_DE[5],
        "answer": "Anna entwickelt sich von einer passiven, schuldbeladenen Person zu einer aktiven, selbstbewussten Frau. Sie lernt, dass Wahrheit nicht immer schwarz-weiß ist und dass Vergebung bei sich selbst beginnt."
    },
    {
        "question": ARONSON_QUESTIONS_DE[6],
        "answer": "Ja, es gibt eine klare Action Line: Annas Suche nach ihrer Schwester. Diese treibt die Handlung von Anfang bis Ende voran und kulminiert in der finalen Konfrontation."
    },
    {
        "question": ARONSON_QUESTIONS_DE[7],
        "answer": "Parallel zur Action Line verläuft eine Relationship Line zwischen Anna und Max, einem Detektiv. Diese Beziehung entwickelt sich von Misstrauen zu Vertrauen und spiegelt Annas innere Entwicklung wider."
    },
    {
        "question": ARONSON_QUESTIONS_DE[8],
        "answer": "Die Balance ist gut: Die äußere Story (Suche nach der Schwester) wird von einer starken inneren Story (Annas Umgang mit Schuld und Selbstzweifel) begleitet. Beide Ebenen informieren und verstärken sich gegenseitig."
    },
    {
        "question": ARONSON_QUESTIONS_DE[9],
        "answer": "Ja, Annas Makel ist ihre Unfähigkeit, sich selbst zu vergeben. Dieser Flaw macht sie menschlich und treibt sowohl ihre irrationale Entschlossenheit als auch ihre Momente der Selbstsabotage an."
    }
]

# Mock Aronson answers in English
mock_aronson_en = [
    {
        "question": ARONSON_QUESTIONS_EN[0],
        "answer": "The protagonist is Anna, a 32-year-old journalist who desperately wants to find the truth about her sister's disappearance. Her motivation is driven by guilt and a desire for redemption."
    },
    {
        "question": ARONSON_QUESTIONS_EN[1],
        "answer": "Several obstacles stand in her way: the police don't believe her, her boss threatens to fire her, and the mysterious stranger seems to know more than he reveals. She also battles her own doubts and fears."
    },
    {
        "question": ARONSON_QUESTIONS_EN[2],
        "answer": "The inciting incident is the mysterious letter Anna receives in Scene 1. It contains a clue about her missing sister's whereabouts and forces Anna to leave her safe world and take action."
    },
    {
        "question": ARONSON_QUESTIONS_EN[3],
        "answer": "Conflicts intensify through increasing threats: Anna is being followed, receives threatening letters, and people around her start behaving strangely. Each answer leads to three new questions."
    },
    {
        "question": ARONSON_QUESTIONS_EN[4],
        "answer": "The climax is the moment when Anna faces her sister and realizes she disappeared voluntarily. Anna must decide whether to publish the truth or protect her sister."
    },
    {
        "question": ARONSON_QUESTIONS_EN[5],
        "answer": "Anna evolves from a passive, guilt-ridden person to an active, confident woman. She learns that truth isn't always black and white and that forgiveness begins with oneself."
    },
    {
        "question": ARONSON_QUESTIONS_EN[6],
        "answer": "Yes, there is a clear action line: Anna's search for her sister. This drives the plot from beginning to end and culminates in the final confrontation."
    },
    {
        "question": ARONSON_QUESTIONS_EN[7],
        "answer": "Parallel to the action line runs a relationship line between Anna and Max, a detective. This relationship develops from mistrust to trust and mirrors Anna's inner development."
    },
    {
        "question": ARONSON_QUESTIONS_EN[8],
        "answer": "The balance is good: the outer story (search for sister) is accompanied by a strong inner story (Anna's dealing with guilt and self-doubt). Both levels inform and reinforce each other."
    },
    {
        "question": ARONSON_QUESTIONS_EN[9],
        "answer": "Yes, Anna's flaw is her inability to forgive herself. This flaw makes her human and drives both her irrational determination and her moments of self-sabotage."
    }
]

def test_german_output():
    """Test German output"""
    print("=" * 80)
    print("TESTING GERMAN OUTPUT (DE)")
    print("=" * 80)
    
    generator = ExcelGenerator(language="DE", mode="story")
    excel_bytes = generator.generate(
        analysis_data=mock_scenes,
        filename="test_screenplay.txt",
        aronson_data=mock_aronson_de
    )
    
    output_path = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/test_output_DE.xlsx"
    with open(output_path, "wb") as f:
        f.write(excel_bytes)
    
    print(f"✅ German Excel created: {output_path}")
    print(f"   Sheets: Scene Analysis, Aronson Analysis, Metadata")
    print(f"   Size: {len(excel_bytes)} bytes")
    print()

def test_english_output():
    """Test English output"""
    print("=" * 80)
    print("TESTING ENGLISH OUTPUT (EN)")
    print("=" * 80)
    
    generator = ExcelGenerator(language="EN", mode="story")
    excel_bytes = generator.generate(
        analysis_data=mock_scenes,
        filename="test_screenplay.txt",
        aronson_data=mock_aronson_en
    )
    
    output_path = "/Users/johanneshoss/Documents/johannes-projects/scene-analyzer/test_output_EN.xlsx"
    with open(output_path, "wb") as f:
        f.write(excel_bytes)
    
    print(f"✅ English Excel created: {output_path}")
    print(f"   Sheets: Scene Analysis, Aronson Analysis, Metadata")
    print(f"   Size: {len(excel_bytes)} bytes")
    print()

def print_preview():
    """Print preview of what will be in the Excel"""
    print("=" * 80)
    print("PREVIEW: ARONSON ANALYSIS SHEET STRUCTURE")
    print("=" * 80)
    print()
    print("Column A: # (Number)")
    print("Column B: Frage / Question (width: 60)")
    print("Column C: Antwort / Answer (width: 80)")
    print()
    print("Example rows (German):")
    print("-" * 80)
    for i, item in enumerate(mock_aronson_de[:3], 1):
        print(f"\nRow {i}:")
        print(f"  #: {i}")
        print(f"  Frage: {item['question']}")
        print(f"  Antwort: {item['answer'][:100]}...")
    print()

if __name__ == "__main__":
    print_preview()
    test_german_output()
    test_english_output()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("Open the generated Excel files to see the formatted output!")
    print("They should have:")
    print("  - Sheet 1: Scene Analysis (with Story columns)")
    print("  - Sheet 2: Aronson Analysis (10 questions + answers)")
    print("  - Sheet 3: Metadata")
