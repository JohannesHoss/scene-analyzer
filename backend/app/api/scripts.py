"""
Scripts API - REST Endpoints für Script-Upload und -Analyse
"""
from fastapi import APIRouter, HTTPException, UploadFile

from app.models.api import ScriptUploadResponse
from app.parsers.exceptions import ParsingError, UnsupportedFormatError
from app.services.script_service import ScriptService

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/upload", response_model=ScriptUploadResponse, status_code=201)
async def upload_script(file: UploadFile):
    """
    Lädt Drehbuch hoch und führt initiales Parsing durch.

    Args:
        file: Hochgeladene Datei (Fountain, Plain Text, etc.)

    Returns:
        Script-Metadaten mit erkannten Szenen

    Raises:
        HTTPException 400: Bei ungültigem oder nicht unterstütztem Format
        HTTPException 413: Bei zu großer Datei
        HTTPException 422: Bei Parsing-Fehlern
        HTTPException 500: Bei internen Fehlern
    """
    # File-Size-Check (50 MB Limit)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    # FastAPI's UploadFile hat kein .size Attribut, daher lesen wir temporär
    content = await file.read()
    await file.seek(0)  # Reset für späteres Lesen

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    try:
        service = ScriptService()
        result = await service.upload_and_parse(file)
        return result

    except UnsupportedFormatError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_format",
                "message": str(e),
                "supported_formats": e.supported_formats,
            },
        )

    except ParsingError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "parsing_error", "message": str(e), "format": e.format_type},
        )

    except Exception as e:
        # Log error (TODO: Add proper logging)
        raise HTTPException(status_code=500, detail="Internal server error")
