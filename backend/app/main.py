from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import FileUploadResponse, AnalysisRequest, AnalysisStatus
from parsers import get_parser
import uuid
import os
from typing import Dict

app = FastAPI(
    title="Scene Analyzer API",
    version="0.2.0",
    description="AI-powered screenplay and treatment analysis tool"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
analysis_jobs: Dict[str, dict] = {}

# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Scene Analyzer API",
        "version": "0.2.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "database": "not_required",
        "storage": "in_memory",
        "active_jobs": len(analysis_jobs)
    }


@app.post("/api/v1/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and validate a screenplay/treatment file"""
    
    # Get file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Validate file type
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size / 1024 / 1024:.1f}MB. Maximum: 50MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Parse and extract scenes immediately
    try:
        parser_class = get_parser(file_ext)
        parser = parser_class(content)
        scenes = parser.extract_scenes()
        detected_language = parser.detect_language()
        
        if not scenes:
            raise HTTPException(
                status_code=400,
                detail="No scenes could be extracted from the file. Please check the format."
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing file: {str(e)}"
        )
    
    # Store in memory
    analysis_jobs[file_id] = {
        "filename": file.filename,
        "file_type": file_ext,
        "size": file_size,
        "status": "uploaded",
        "scenes": scenes,
        "total_scenes": len(scenes),
        "detected_language": detected_language,
        "progress": 0
    }
    
    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=file_size,
        file_type=file_ext,
        status="uploaded"
    )


@app.get("/api/v1/status/{job_id}", response_model=AnalysisStatus)
async def get_status(job_id: str):
    """Get analysis status for a job"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    return AnalysisStatus(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        current_scene=job.get("current_scene"),
        total_scenes=job.get("total_scenes"),
        error=job.get("error")
    )


@app.get("/api/v1/scenes/{job_id}")
async def get_scenes(job_id: str):
    """Get extracted scenes for inspection (debug endpoint)"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "total_scenes": job["total_scenes"],
        "detected_language": job.get("detected_language", "unknown"),
        "scenes": job.get("scenes", [])
    }
