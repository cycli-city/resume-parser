
"""
AI-Powered Resume Parser
=========================
FastAPI application that accepts PDF resumes, extracts structured
information from them using an LLM (Anthropic Claude), and exposes
that data through a small REST API.
 
Endpoints
---------
POST /resumes/upload      -> upload a PDF resume, parse it, store it
GET  /candidates          -> list all parsed candidates (paginated)
GET  /candidates/{id}     -> full structured details for one candidate
 
Auth
----
All endpoints (except /health) require an API key passed in the
`X-API-Key` header. Keys are configured via the API_KEYS env var
(comma-separated). See app/auth.py.
 
Run locally
-----------
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    export API_KEYS=devkey123
    uvicorn app.main:app --reload
"""
 
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()
 
import json
import logging
from datetime import datetime, timezone
from typing import Optional
 
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
 
from app.auth import require_api_key
from app.db import init_db, get_session, Candidate
from app.pdf_utils import extract_text_from_pdf, PDFExtractionError
from app.llm import parse_resume_with_llm, LLMParsingError
from app.schemas import CandidateListResponse, CandidateSummary, CandidateDetail, UploadResponse
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resume_parser")
 
app = FastAPI(
    title="AI-Powered Resume Parser",
    description="Upload PDF resumes and extract structured candidate data using an LLM.",
    version="1.0.0",
)
 
 
@app.on_event("startup")
def on_startup() -> None:
    init_db()
 
 
@app.get("/health", tags=["meta"])
def health() -> dict:
    """Unauthenticated health check."""
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}
 
 
@app.post(
    "/resumes/upload",
    response_model=UploadResponse,
    tags=["resumes"],
    dependencies=[Depends(require_api_key)],
)
async def upload_resume(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a PDF resume. The file is parsed for text, sent to an LLM
    for structured extraction, and the result is stored in the database.
    """
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
 
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
 
    try:
        text = extract_text_from_pdf(raw_bytes)
    except PDFExtractionError as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {e}")
 
    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in PDF (it may be a scanned image).")
 
    try:
        structured = parse_resume_with_llm(text)
    except LLMParsingError as e:
        raise HTTPException(status_code=502, detail=f"LLM parsing failed: {e}")
 
    with get_session() as session:
        candidate = Candidate(
            filename=file.filename or "resume.pdf",
            full_name=structured.get("full_name"),
            email=structured.get("email"),
            phone=structured.get("phone"),
            location=structured.get("location"),
            summary=structured.get("summary"),
            total_experience_years=structured.get("total_experience_years"),
            skills_json=json.dumps(structured.get("skills", [])),
            education_json=json.dumps(structured.get("education", [])),
            experience_json=json.dumps(structured.get("experience", [])),
            raw_text=text,
            created_at=datetime.now(timezone.utc),
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
 
        return UploadResponse(
            id=candidate.id,
            filename=candidate.filename,
            full_name=candidate.full_name,
            message="Resume parsed and stored successfully.",
        )
 
 
@app.get(
    "/candidates",
    response_model=CandidateListResponse,
    tags=["candidates"],
    dependencies=[Depends(require_api_key)],
)
def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Filter by name, email, or skill substring"),
) -> CandidateListResponse:
    """List parsed candidates with basic pagination and optional search."""
    with get_session() as session:
        query = session.query(Candidate)
        if search:
            like = f"%{search}%"
            query = query.filter(
                (Candidate.full_name.ilike(like))
                | (Candidate.email.ilike(like))
                | (Candidate.skills_json.ilike(like))
            )
 
        total = query.count()
        rows = (
            query.order_by(Candidate.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
 
        items = [
            CandidateSummary(
                id=c.id,
                full_name=c.full_name,
                email=c.email,
                phone=c.phone,
                location=c.location,
                total_experience_years=c.total_experience_years,
                skills=json.loads(c.skills_json or "[]"),
                created_at=c.created_at,
            )
            for c in rows
        ]
 
        return CandidateListResponse(total=total, page=page, page_size=page_size, items=items)
 
 
@app.get(
    "/candidates/{candidate_id}",
    response_model=CandidateDetail,
    tags=["candidates"],
    dependencies=[Depends(require_api_key)],
)
def get_candidate(candidate_id: int) -> CandidateDetail:
    """Full structured details for a single candidate, including raw resume text."""
    with get_session() as session:
        candidate = session.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found.")
 
        return CandidateDetail(
            id=candidate.id,
            filename=candidate.filename,
            full_name=candidate.full_name,
            email=candidate.email,
            phone=candidate.phone,
            location=candidate.location,
            summary=candidate.summary,
            total_experience_years=candidate.total_experience_years,
            skills=json.loads(candidate.skills_json or "[]"),
            education=json.loads(candidate.education_json or "[]"),
            experience=json.loads(candidate.experience_json or "[]"),
            raw_text=candidate.raw_text,
            created_at=candidate.created_at,
        )
 
 
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
 