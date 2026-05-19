import asyncio
import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.db.mongo import (
    get_document_by_id,
    get_student_documents,
    save_document_metadata,
)

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip() or "document"
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", name)


def _document_response(doc: dict) -> dict:
    return {
        "id": doc["_id"],
        "student_id": doc["student_id"],
        "filename": doc["filename"],
        "content_type": doc.get("content_type") or "application/octet-stream",
        "size": doc["size"],
        "uploaded_at": doc["uploaded_at"],
        "download_url": f"/documents/{doc['_id']}/download",
    }


async def _write_bytes(path: Path, content: bytes) -> None:
    await asyncio.to_thread(path.write_bytes, content)


@router.post("/upload")
async def upload_document(
    student_id: str = Form(...),
    file: UploadFile = File(...),
):
    original_name = _safe_filename(file.filename or "document")
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension or 'unknown'}",
        )

    content = await file.read()
    max_bytes = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than {settings.MAX_DOCUMENT_SIZE_MB} MB.",
        )

    storage_dir = Path(settings.DOCUMENT_STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex}{extension}"
    stored_path = storage_dir / stored_name
    await _write_bytes(stored_path, content)

    try:
        doc = await save_document_metadata({
            "student_id": student_id,
            "filename": original_name,
            "stored_name": stored_name,
            "storage_path": str(stored_path),
            "content_type": file.content_type or "application/octet-stream",
            "size": len(content),
        })
    except Exception:
        if stored_path.exists():
            os.remove(stored_path)
        raise

    return {
        "status": "success",
        "document": _document_response(doc),
    }


@router.get("")
async def list_documents(student_id: str):
    docs = await get_student_documents(student_id)
    return [_document_response(doc) for doc in docs]


@router.get("/{document_id}/download")
async def download_document(document_id: str):
    doc = await get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    path = Path(doc["storage_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Stored file is missing.")

    return FileResponse(
        path=path,
        media_type=doc.get("content_type") or "application/octet-stream",
        filename=doc["filename"],
    )
