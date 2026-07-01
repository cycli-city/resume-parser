"""Pydantic models for API responses."""
 
from __future__ import annotations
 
from datetime import datetime
from typing import Optional
 
from pydantic import BaseModel
 
 
class UploadResponse(BaseModel):
    id: int
    filename: str
    full_name: Optional[str] = None
    message: str
 
 
class CandidateSummary(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    total_experience_years: Optional[float] = None
    skills: list[str] = []
    created_at: datetime
 
 
class CandidateListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CandidateSummary]
 
 
class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None
 
 
class ExperienceItem(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
 
 
class CandidateDetail(BaseModel):
    id: int
    filename: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    skills: list[str] = []
    education: list[dict] = []
    experience: list[dict] = []
    raw_text: Optional[str] = None
    created_at: datetime
 