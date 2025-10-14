"""
API Models - Request/Response Models für FastAPI
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.scene import Scene


class ScriptFormat(str, Enum):
    """Unterstützte Drehbuch-Formate."""

    FOUNTAIN = "fountain"
    PLAINTEXT = "plaintext"
    PDF = "pdf"
    FDX = "fdx"
    DOCX = "docx"


class ScriptUploadResponse(BaseModel):
    """Response nach Script-Upload."""

    script_id: str = Field(description="Eindeutige Script-ID (UUID)")
    filename: str = Field(description="Original-Dateiname")
    format: str = Field(description="Erkanntes Format")
    scenes_count: int = Field(ge=0, description="Anzahl erkannter Szenen")
    pages: int = Field(ge=0, description="Geschätzte Seitenzahl")
    upload_time: datetime = Field(description="Upload-Zeitstempel")

    model_config = {
        "json_schema_extra": {
            "example": {
                "script_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "my-script.fountain",
                "format": "fountain",
                "scenes_count": 42,
                "pages": 90,
                "upload_time": "2025-10-14T16:30:00Z",
            }
        }
    }


class AnalysisRequest(BaseModel):
    """Request für Szenen-Analyse."""

    parameters: list[str] = Field(
        description="Liste der zu analysierenden Parameter",
        examples=[
            [
                "scene_number",
                "int_ext",
                "location",
                "time",
                "characters",
                "page_number",
                "estimated_length",
            ]
        ],
    )


class AnalysisResponse(BaseModel):
    """Response nach Szenen-Analyse."""

    analysis_id: str = Field(description="Eindeutige Analyse-ID (UUID)")
    script_id: str = Field(description="Referenz zur Script-ID")
    scenes: list[Scene] = Field(description="Liste der analysierten Szenen")
    total_scenes: int = Field(ge=0, description="Gesamtzahl Szenen")
    total_pages: int = Field(ge=0, description="Gesamtzahl Seiten")
    total_runtime_estimate: int = Field(ge=0, description="Geschätzte Gesamtlänge in Minuten")
    created_at: datetime = Field(description="Analyse-Zeitstempel")

    model_config = {
        "json_schema_extra": {
            "example": {
                "analysis_id": "660e8400-e29b-41d4-a716-446655440000",
                "script_id": "550e8400-e29b-41d4-a716-446655440000",
                "scenes": [
                    {
                        "scene_number": 1,
                        "int_ext": "INT",
                        "location": "WOHNUNG BERLIN",
                        "time": "TAG",
                        "characters": ["ANNA", "PETER"],
                        "page_number": 1,
                        "estimated_length": 2.5,
                    }
                ],
                "total_scenes": 42,
                "total_pages": 90,
                "total_runtime_estimate": 90,
                "created_at": "2025-10-14T16:30:00Z",
            }
        }
    }
