"""
Unit Tests für PDF Parser
"""
from io import BytesIO

import pytest
from PyPDF2 import PdfWriter

from app.parsers.pdf_parser import PDFParser


@pytest.fixture
def pdf_parser():
    return PDFParser()


@pytest.fixture
def simple_pdf_content():
    """Creates a simple PDF with scene headings."""
    writer = PdfWriter()
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Add scene headings
    can.drawString(100, 750, "INT. TEST LOCATION - DAY")
    can.drawString(100, 700, "Action description here.")
    can.drawString(100, 650, "CHARACTER")
    can.drawString(100, 630, "Dialog here.")

    can.save()
    packet.seek(0)

    # Read the PDF back
    from PyPDF2 import PdfReader

    existing_pdf = PdfReader(packet)
    writer.add_page(existing_pdf.pages[0])

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class TestPDFParser:
    def test_can_parse_pdf_extension(self, pdf_parser):
        assert pdf_parser.can_parse("script.pdf", b"random")

    def test_can_parse_pdf_magic_bytes(self, pdf_parser):
        assert pdf_parser.can_parse("unknown.txt", b"%PDF-1.4\n...")

    def test_cannot_parse_invalid(self, pdf_parser):
        assert not pdf_parser.can_parse("script.txt", b"plain text")

    @pytest.mark.skip("Requires reportlab which might not be installed")
    def test_parse_simple_pdf(self, pdf_parser, simple_pdf_content):
        """Test parsing a simple PDF with one scene."""
        scenes = pdf_parser.parse(simple_pdf_content)
        assert len(scenes) >= 1

    def test_normalize_int_ext_de(self, pdf_parser):
        """Test German INT/EXT normalization."""
        assert pdf_parser._normalize_int_ext("INNEN") == "INT"
        assert pdf_parser._normalize_int_ext("AUSSEN") == "EXT"
        assert pdf_parser._normalize_int_ext("INNEN/AUSSEN") == "INT/EXT"

    def test_normalize_int_ext_en(self, pdf_parser):
        """Test English INT/EXT normalization."""
        assert pdf_parser._normalize_int_ext("INT") == "INT"
        assert pdf_parser._normalize_int_ext("EXT") == "EXT"
        assert pdf_parser._normalize_int_ext("INT/EXT") == "INT/EXT"

    def test_extract_scenes_from_text(self, pdf_parser):
        """Test scene extraction from plain text."""
        text = """INT. ROOM A - DAY

Action here.

CHARACTER
Dialog here.

EXT. PARK - NIGHT

More action."""

        scenes = pdf_parser._extract_scenes_from_text(text)
        assert len(scenes) == 2
        assert scenes[0].int_ext == "INT"
        assert scenes[0].location == "ROOM A"
        assert scenes[0].time == "DAY"
        assert scenes[1].int_ext == "EXT"
        assert scenes[1].location == "PARK"

    def test_extract_characters(self, pdf_parser):
        """Test character extraction."""
        content = """ANNA
Hello!

PETER
Hi there!"""

        chars = pdf_parser._extract_characters(content)
        assert "ANNA" in chars
        assert "PETER" in chars
