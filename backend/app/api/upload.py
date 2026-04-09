"""File upload API endpoint for chat attachments."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..schemas import ContextMode

router = APIRouter()

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 
    'mp3', 'mp4', 'wav', 'xlsx', 'csv', 'json', 'xml'
}

def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix[1:].lower()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

@router.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = "default",
    context_mode: str = "neutral"
):
    """Upload a file for chat analysis."""
    
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Validate file extension
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Generate unique filename
        file_extension = get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}_{session_id}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads") / session_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / unique_filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Return success response
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "session_id": session_id,
            "context_mode": context_mode,
            "uploaded_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/api/uploads/{session_id}")
async def list_uploads(session_id: str):
    """List uploaded files for a session."""
    try:
        upload_dir = Path("uploads") / session_id
        if not upload_dir.exists():
            return {"files": []}
        
        files = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )

@router.delete("/api/uploads/{session_id}/{filename}")
async def delete_upload(session_id: str, filename: str):
    """Delete an uploaded file."""
    try:
        file_path = Path("uploads") / session_id / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        file_path.unlink()
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )