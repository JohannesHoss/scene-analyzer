"""
Unit Tests für Fountain-Parser
"""
import pytest

from app.parsers.exceptions import ParsingError
from app.parsers.fountain_parser import FountainParser


class TestFountainParser:
    """Tests für FountainParser."""

    def test_can_parse_fountain_extension(self):
        """Test: Parser erkennt .fountain Extension."""
        parser = FountainParser()
        assert parser.can_parse("script.fountain", b"random content")

    def test_can_parse_fountain_content(self, simple_fountain_content):
        """Test: Parser erkennt Fountain-Content."""
        parser = FountainParser()
        assert parser.can_parse("unknown.txt", simple_fountain_content)

    def test_cannot_parse_invalid_content(self, invalid_content):
        """Test: Parser lehnt ungültigen Content ab."""
        parser = FountainParser()
        assert not parser.can_parse("invalid.txt", invalid_content)

    def test_parse_simple_scene(self, simple_fountain_content):
        """Test: Einfache Szene parsen."""
        parser = FountainParser()
        scenes = parser.parse(simple_fountain_content)

        assert len(scenes) == 1
        scene = scenes[0]
        assert scene.scene_number == 1
        assert scene.int_ext == "INT"
        assert scene.location == "TEST LOCATION"
        assert scene.time == "DAY"
        assert scene.page_number >= 1

    def test_parse_multi_scene(self, multi_scene_fountain):
        """Test: Mehrere Szenen parsen."""
        parser = FountainParser()
        scenes = parser.parse(multi_scene_fountain)

        assert len(scenes) == 3

        # Erste Szene
        assert scenes[0].scene_number == 1
        assert scenes[0].int_ext == "INT"
        assert scenes[0].location == "ROOM A"
        assert scenes[0].time == "DAY"

        # Zweite Szene
        assert scenes[1].scene_number == 2
        assert scenes[1].int_ext == "EXT"
        assert scenes[1].location == "ROOM B"
        assert scenes[1].time == "NIGHT"

        # Dritte Szene
        assert scenes[2].scene_number == 3
        assert scenes[2].int_ext == "INT/EXT"  # Normalisiert
        assert scenes[2].location == "ROOM C"
        assert scenes[2].time == "DAWN"

    def test_parse_sample_script(self, sample_fountain_content):
        """Test: Komplettes Sample-Script parsen."""
        parser = FountainParser()
        scenes = parser.parse(sample_fountain_content)

        # Sample hat 4 Szenen
        assert len(scenes) == 4

        # Prüfe erste Szene
        first_scene = scenes[0]
        assert first_scene.scene_number == 1
        assert first_scene.int_ext == "INT"
        assert "APARTMENT BERLIN" in first_scene.location
        assert first_scene.time == "DAY"

        # Prüfe letzte Szene
        last_scene = scenes[-1]
        assert last_scene.scene_number == 4
        assert last_scene.int_ext == "INT"
        assert "APARTMENT BERLIN" in last_scene.location
        assert last_scene.time == "NIGHT"

    def test_parse_invalid_encoding(self):
        """Test: Fehlerhafte Encoding wirft Exception."""
        parser = FountainParser()
        # Ungültiges UTF-8
        with pytest.raises(ParsingError):
            parser.parse(b"\xff\xfe invalid utf-8")

    def test_estimate_page_numbers(self, sample_fountain_content):
        """Test: Seitenzahlen werden geschätzt."""
        parser = FountainParser()
        scenes = parser.parse(sample_fountain_content)

        # Alle Szenen sollten Seitenzahlen haben
        for scene in scenes:
            assert scene.page_number >= 1

        # Spätere Szenen sollten höhere Seitenzahlen haben
        assert scenes[-1].page_number >= scenes[0].page_number

    def test_raw_content_excluded(self, simple_fountain_content):
        """Test: raw_content wird aus JSON excluded."""
        parser = FountainParser()
        scenes = parser.parse(simple_fountain_content)

        scene = scenes[0]
        # raw_content sollte gesetzt sein (intern)
        assert scene.raw_content is not None
        assert len(scene.raw_content) > 0

        # Aber nicht in JSON-Export
        json_data = scene.model_dump()
        assert "raw_content" not in json_data

    def test_int_ext_normalization(self):
        """Test: INT./EXT Varianten werden normalisiert."""
        parser = FountainParser()

        content = b"""INT./EXT. LOCATION - DAY
Test
I/E. LOCATION2 - NIGHT
Test2
INT/EXT LOCATION3 - DAY
Test3
"""
        scenes = parser.parse(content)

        # Alle sollten zu INT/EXT normalisiert werden
        assert scenes[0].int_ext == "INT/EXT"
        assert scenes[1].int_ext == "INT/EXT"
        assert scenes[2].int_ext == "INT/EXT"

    def test_missing_time(self):
        """Test: Szenen ohne Zeit-Angabe."""
        parser = FountainParser()
        content = b"INT. LOCATION\n\nAction."

        scenes = parser.parse(content)
        assert len(scenes) == 1
        assert scenes[0].time is None

    def test_empty_content(self):
        """Test: Leerer Content."""
        parser = FountainParser()
        scenes = parser.parse(b"")

        assert len(scenes) == 0


class TestCharacterExtraction:
    """Tests für Charakter-Extraktion."""

    def test_extract_characters_basic(self):
        """Test: Basis-Charakterextraktion."""
        parser = FountainParser()
        content = """ANNA
Hello!

PETER
Hi there!

ANNA
How are you?
"""
        characters = parser._extract_characters(content)

        assert "ANNA" in characters
        assert "PETER" in characters
        assert len(characters) == 2

    def test_extract_characters_with_parentheticals(self):
        """Test: Charaktere mit Parentheticals."""
        parser = FountainParser()
        content = """ANNA (O.S.)
Hello!

PETER (V.O.)
Hi!
"""
        characters = parser._extract_characters(content)

        # Parentheticals sollten entfernt werden
        assert "ANNA" in characters
        assert "PETER" in characters
        assert "ANNA (O.S.)" not in characters

    def test_extract_characters_umlauts(self):
        """Test: Deutsche Umlaute in Namen."""
        parser = FountainParser()
        content = """MÜLLER
Hello!

SCHRÖDER
Hi!
"""
        characters = parser._extract_characters(content)

        assert "MÜLLER" in characters
        assert "SCHRÖDER" in characters

    def test_extract_characters_filters(self):
        """Test: Filter für ungültige Charaktere."""
        parser = FountainParser()
        content = """A
Too short.

AVERYLONGNAMETHATISMORETHAN30CHARACTERSLONG
Too long.

123
Numbers only.

VALID NAME
This should work.
"""
        characters = parser._extract_characters(content)

        # Nur VALID NAME sollte akzeptiert werden
        assert "VALID NAME" in characters
        assert "A" not in characters  # Zu kurz
        assert "123" not in characters  # Nur Zahlen
