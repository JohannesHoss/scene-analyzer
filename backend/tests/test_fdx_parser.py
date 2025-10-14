"""
Unit Tests für FDX Parser
"""
import pytest

from app.parsers.fdx_parser import FDXParser


@pytest.fixture
def fdx_parser():
    return FDXParser()


@pytest.fixture
def simple_fdx_content():
    """Simple Final Draft XML structure."""
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script" Template="No" Version="1">
<Content>
<Paragraph Type="Scene Heading">
<Text>INT. TEST LOCATION - DAY</Text>
</Paragraph>
<Paragraph Type="Action">
<Text>Action description here.</Text>
</Paragraph>
<Paragraph Type="Character">
<Text>CHARACTER</Text>
</Paragraph>
<Paragraph Type="Dialogue">
<Text>Dialog here.</Text>
</Paragraph>
<Paragraph Type="Scene Heading">
<Text>EXT. PARK - NIGHT</Text>
</Paragraph>
<Paragraph Type="Action">
<Text>More action.</Text>
</Paragraph>
</Content>
</FinalDraft>"""


class TestFDXParser:
    def test_can_parse_fdx_extension(self, fdx_parser):
        assert fdx_parser.can_parse("script.fdx", b"random")

    def test_can_parse_fdx_content(self, fdx_parser):
        assert fdx_parser.can_parse("unknown.txt", b"<?xml...<FinalDraft>")

    def test_cannot_parse_invalid(self, fdx_parser):
        assert not fdx_parser.can_parse("script.txt", b"plain text")

    def test_parse_simple_fdx(self, fdx_parser, simple_fdx_content):
        """Test parsing simple FDX with 2 scenes."""
        scenes = fdx_parser.parse(simple_fdx_content)

        assert len(scenes) == 2

        # First scene
        assert scenes[0].scene_number == 1
        assert scenes[0].int_ext == "INT"
        assert scenes[0].location == "TEST LOCATION"
        assert scenes[0].time == "DAY"

        # Second scene
        assert scenes[1].scene_number == 2
        assert scenes[1].int_ext == "EXT"
        assert scenes[1].location == "PARK"
        assert scenes[1].time == "NIGHT"

    def test_normalize_int_ext_de(self, fdx_parser):
        """Test German INT/EXT normalization."""
        assert fdx_parser._normalize_int_ext("INNEN") == "INT"
        assert fdx_parser._normalize_int_ext("AUSSEN") == "EXT"
        assert fdx_parser._normalize_int_ext("INNEN/AUSSEN") == "INT/EXT"

    def test_normalize_int_ext_en(self, fdx_parser):
        """Test English INT/EXT normalization."""
        assert fdx_parser._normalize_int_ext("INT") == "INT"
        assert fdx_parser._normalize_int_ext("EXT") == "EXT"
        assert fdx_parser._normalize_int_ext("INT/EXT") == "INT/EXT"

    def test_extract_characters(self, fdx_parser):
        """Test character extraction."""
        content = """ANNA
Hello!

PETER
Hi there!"""

        chars = fdx_parser._extract_characters(content)
        assert "ANNA" in chars
        assert "PETER" in chars

    def test_parse_german_fdx(self, fdx_parser):
        """Test parsing German FDX."""
        german_fdx = b"""<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script">
<Content>
<Paragraph Type="Scene Heading">
<Text>INNEN. WOHNUNG - TAG</Text>
</Paragraph>
<Paragraph Type="Action">
<Text>Anna betritt die Wohnung.</Text>
</Paragraph>
</Content>
</FinalDraft>"""

        scenes = fdx_parser.parse(german_fdx)
        assert len(scenes) == 1
        assert scenes[0].int_ext == "INT"
        assert scenes[0].location == "WOHNUNG"
        assert scenes[0].time == "TAG"
