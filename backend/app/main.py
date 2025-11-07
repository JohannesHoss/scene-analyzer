from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from models.schemas import FileUploadResponse, AnalysisRequest, AnalysisStatus
from parsers import get_parser
from analyzer import OpenRouterClient, SceneAnalyzer
from excel import ExcelGenerator
import uuid
import os
import asyncio
from typing import Dict
from datetime import datetime

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


@app.post("/api/v1/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start AI analysis of uploaded file"""
    
    if request.file_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="File not found")
    
    job = analysis_jobs[request.file_id]
    
    if job["status"] != "uploaded":
        raise HTTPException(status_code=400, detail=f"Job already {job['status']}")
    
    # Update job with analysis parameters
    job.update({
        "output_language": request.output_language,
        "model": request.model,
        "mode": request.mode,
        "protagonist_count": request.protagonist_count,
        "status": "queued"
    })
    
    # Estimate cost
    try:
        client = OpenRouterClient()
        analyzer = SceneAnalyzer(client, request.mode, request.output_language, request.model)
        estimated_cost = analyzer.estimate_cost(job["total_scenes"])
        job["estimated_cost"] = estimated_cost
    except Exception as e:
        job["estimated_cost"] = 0.0
    
    # Start analysis in background
    background_tasks.add_task(process_analysis, request.file_id)
    
    return {
        "job_id": request.file_id,
        "status": "queued",
        "total_scenes": job["total_scenes"],
        "estimated_cost": job.get("estimated_cost", 0.0)
    }


async def process_analysis(job_id: str):
    """Background task to process scene analysis"""
    try:
        job = analysis_jobs[job_id]
        job["status"] = "processing"
        
        # Initialize analyzer
        client = OpenRouterClient()
        analyzer = SceneAnalyzer(
            client,
            job["mode"],
            job["output_language"],
            job["model"]
        )
        
        # Analyze scenes
        results = await analyzer.analyze_all_scenes(
            job["scenes"],
            analysis_jobs,
            job_id
        )
        
        # Store results
        job["results"] = results
        job["status"] = "completed"
        job["progress"] = 100
        
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["progress"] = 0


@app.get("/api/v1/results/{job_id}")
async def get_results(job_id: str):
    """Get analysis results"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Current status: {job['status']}"
        )
    
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "mode": job["mode"],
        "language": job["output_language"],
        "model": job["model"],
        "total_scenes": len(job["results"]),
        "results": job["results"]
    }


@app.get("/api/v1/download/{job_id}")
async def download_excel(job_id: str):
    """Download analysis as Excel file"""
    
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Current status: {job['status']}"
        )
    
    # Generate Excel
    generator = ExcelGenerator(
        language=job["output_language"],
        mode=job["mode"]
    )
    
    excel_data = generator.generate(
        analysis_data=job["results"],
        filename=job["filename"]
    )
    
    # Create filename
    base_name = os.path.splitext(job["filename"])[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_filename = f"{base_name}_analysis_{timestamp}.xlsx"
    
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{download_filename}"'
        }
    )
