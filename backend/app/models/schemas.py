from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    file_id: str
    filename: str
    size: int
    file_type: str
    status: str = "uploaded"


class AnalysisRequest(BaseModel):
    """Request model for starting analysis"""
    file_id: str
    output_language: str = Field(..., pattern="^(DE|EN)$")
    model: str
    mode: str = Field(..., pattern="^(standard|tatort|story|combined)$")
    protagonist_count: Optional[int] = Field(default=1, ge=1, le=5)


class AnalysisStatus(BaseModel):
    """Response model for analysis status"""
    job_id: str
    status: str  # uploaded, processing, analyzing, completed, error
    progress: int = Field(default=0, ge=0, le=100)
    current_scene: Optional[int] = None
    total_scenes: Optional[int] = None
    error: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds


class SceneData(BaseModel):
    """Model for extracted scene data"""
    number: int
    int_ext: Optional[str] = None
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    text: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
