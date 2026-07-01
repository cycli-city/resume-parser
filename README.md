AI-Powered Resume Parser

A FastAPI application that accepts PDF resumes, extracts text, and uses Groq LLaMA 3.3 70B to parse structured candidate information. All endpoints are protected with API key authentication.

Live Demo


Swagger UI: https://resume-parser-75zn.onrender.com/docs
Base URL: https://resume-parser-75zn.onrender.com


Features


Upload PDF resumes and extract structured data using an LLM
Candidate list API with pagination and search
Candidate details API with full profile
API key authentication on all endpoints
SQLite database for persistent storage


Tech Stack


Framework: FastAPI
LLM: Groq API (LLaMA 3.3 70B)
PDF Extraction: pdfplumber
Database: SQLite + SQLAlchemy
Deployment: Render


API Endpoints

MethodEndpointAuthDescriptionGET/healthNoHealth checkPOST/resumes/uploadYesUpload a PDF resumeGET/candidatesYesList all candidatesGET/candidates/{id}YesFull candidate details

Setup & Run Locally

1. Clone the repository

bashgit clone https://github.com/cycli-city/resume-parser.git
cd resume-parser

2. Install dependencies

bashpip install -r requirements.txt

3. Create a .env file

GROQ_API_KEY=your_groq_api_key_here
API_KEYS=devkey123

4. Run the server

bashpython -m uvicorn app.main:app --reload

5. Open Swagger UI

Visit http://localhost:8000/docs

Authentication

All endpoints except /health require an X-API-Key header.

X-API-Key: devkey123

Example Usage

Upload a Resume

bashcurl -X POST https://resume-parser-75zn.onrender.com/resumes/upload \
  -H "X-API-Key: devkey123" \
  -F "file=@resume.pdf"

List Candidates

bashcurl https://resume-parser-75zn.onrender.com/candidates \
  -H "X-API-Key: devkey123"

Get Candidate Details

bashcurl https://resume-parser-75zn.onrender.com/candidates/1 \
  -H "X-API-Key: devkey123"

Project Structure

resume-parser/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI routes
│   ├── auth.py        # API key authentication
│   ├── db.py          # Database models
│   ├── llm.py         # Groq LLM integration
│   ├── pdf_utils.py   # PDF text extraction
│   └── schemas.py     # Pydantic response schemas
├── .env               # Environment variables (not committed)
├── .python-version    # Python 3.11.9
├── requirements.txt
└── README.md