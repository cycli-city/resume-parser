"""
Structured resume extraction via Groq API (direct HTTP, no SDK).
"""
 
from __future__ import annotations
 
import json
import os
import re
 
import requests
 
MODEL = os.environ.get("RESUME_PARSER_MODEL", "llama-3.3-70b-versatile")
 
SYSTEM_PROMPT = """You are a resume parsing engine. You will be given the raw text \
extracted from a PDF resume. Extract structured information and respond with ONLY a \
single JSON object -- no markdown fences, no commentary, no preamble.
 
JSON schema to follow exactly:
{
  "full_name": string or null,
  "email": string or null,
  "phone": string or null,
  "location": string or null,
  "summary": string or null (2-3 sentence professional summary, write one if absent),
  "total_experience_years": number or null (best estimate, e.g. 3.5),
  "skills": [string, ...],
  "education": [
    {"institution": string, "degree": string or null, "field": string or null, "start_year": string or null, "end_year": string or null}
  ],
  "experience": [
    {"company": string, "title": string or null, "start_date": string or null, "end_date": string or null, "description": string or null}
  ]
}
 
Rules:
- If a field cannot be determined, use null (or an empty array for list fields). Never invent data.
- Dates should be kept in whatever granularity the resume provides (e.g. "2021", "Jan 2021").
- Output must be valid JSON parseable by a standard JSON parser.
"""
 
 
class LLMParsingError(Exception):
    pass
 
 
def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))
 
 
def parse_resume_with_llm(resume_text: str, max_chars: int = 15000) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise LLMParsingError("GROQ_API_KEY is not set.")
 
    truncated = resume_text[:max_chars]
 
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 2000,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": truncated},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        raw_text = response.json()["choices"][0]["message"]["content"]
        return _extract_json(raw_text)
    except json.JSONDecodeError as e:
        raise LLMParsingError(f"Model did not return valid JSON: {e}") from e
    except Exception as e:
        raise LLMParsingError(str(e)) from e