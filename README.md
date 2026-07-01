AI-Powered Resume Parser

FastAPI service that accepts PDF resumes, extracts text, sends it to Claude
for structured extraction, and stores/serves the result through a REST API.
API-key auth is enforced on every data endpoint.

Setup

bashpip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # required for parsing
export API_KEYS=devkey123                # comma-separated list of valid client keys
uvicorn app.main:app --reload

Visit http://localhost:8000/docs for interactive Swagger UI (use the
"Authorize" button to set X-API-Key).

Endpoints

MethodPathAuthDescriptionGET/healthnoLiveness checkPOST/resumes/uploadyesUpload a PDF, parse it, store the candidateGET/candidatesyesList candidates (page, page_size, search)GET/candidates/{id}yesFull structured detail incl. raw resume text

Auth header: X-API-Key: <one of API_KEYS>

Example

bashcurl -X POST http://localhost:8000/resumes/upload \
  -H "X-API-Key: devkey123" \
  -F "file=@resume.pdf"

curl http://localhost:8000/candidates?search=python \
  -H "X-API-Key: devkey123"

curl http://localhost:8000/candidates/1 \
  -H "X-API-Key: devkey123"

Design notes


PDF extraction: pdfplumber pulls raw text per page. Scanned/image-only
PDFs (no extractable text layer) return a 422 — add OCR (e.g. pytesseract)
if you need that case.
LLM extraction: a single Claude call (app/llm.py) with a strict
JSON-only system prompt defines the schema (name, email, phone, location,
summary, years of experience, skills, education, experience). The model is
claude-sonnet-4-6 by default, overridable via RESUME_PARSER_MODEL.
Storage: SQLite via SQLAlchemy (resumes.db, path overridable via
RESUME_DB_PATH). Structured lists (skills/education/experience) are
stored as JSON text columns — fine at this scale; move to Postgres +
native JSON/JSONB if you need concurrent writers or querying inside the
arrays.
Auth: deliberately simple shared-secret API keys via header
(app/auth.py), matching what's needed for an internal/admin tool. Swap
for JWT/OAuth2 if external clients need scoped tokens — only auth.py
needs to change since every route just depends on require_api_key.


Tests run during development

Verified with FastAPI's TestClient:


health check unauthenticated
missing/invalid API key correctly rejected (422 / 401)
full upload → list → detail flow against a generated sample PDF, with the
LLM call mocked (no live API key in the build sandbox) to confirm PDF
extraction, DB writes, and response shaping are all correct.


You'll want to do one live run with a real ANTHROPIC_API_KEY and an actual
resume PDF before treating this as fully verified end-to-end.