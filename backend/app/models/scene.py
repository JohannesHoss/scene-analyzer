"""
Scene Model - Domain Model für eine Drehbuch-Szene
"""
from typing import Optional
from pydantic import BaseModel, Field


class Scene(BaseModel):
    """Domain-Model für eine Szene."""

    scene_number: int = Field(ge=1, description="Szenen-Nummer (ab 1)")
    int_ext: Optional[str] = Field(None, description="INT, EXT, oder INT/EXT")
    location: Optional[str] = Field(None, max_length=200)
    time: Optional[str] = Field(None, description="TAG, NACHT, etc.")
    characters: list[str] = Field(default_factory=list)
    page_number: int = Field(ge=1, description="Start-Seite der Szene")
    estimated_length: Optional[float] = Field(None, ge=0, description="Geschätzte Länge in Minuten")

    # Intern (nicht in API-Response)
    raw_content: Optional[str] = Field(None, exclude=True, description="Roher Szenen-Content")

    model_config = {
        "json_schema_extra": {
            "example": {
                "scene_number": 1,
                "int_ext": "INT",
                "location": "WOHNUNG BERLIN",
                "time": "TAG",
                "characters": ["ANNA", "PETER"],
                "page_number": 1,
                "estimated_length": 2.5,
            }
        }
    }
