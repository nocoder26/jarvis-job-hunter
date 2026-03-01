from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Company schemas
class CompanyBase(BaseModel):
    name: str
    domain: Optional[str] = None
    website_url: Optional[str] = None
    is_enisa_certified: bool = False
    is_startup_law: bool = False
    funding_stage: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: UUID
    enriched_at: Optional[datetime] = None
    created_at: datetime


# Job schemas
class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    application_url: Optional[str] = None


class JobResponse(JobBase):
    id: UUID
    external_id: Optional[str] = None
    source: str
    company_id: Optional[UUID] = None
    ats_type: Optional[str] = None
    posted_at: Optional[datetime] = None
    discovered_at: datetime
    status: str
    companies: Optional[CompanyResponse] = None
    job_analysis: Optional["JobAnalysisResponse"] = None


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int


# Job Analysis schemas
class JobAnalysisResponse(BaseModel):
    id: Optional[UUID] = None
    job_id: Optional[UUID] = None
    fit_score: int
    spanish_required: bool
    visa_status: str
    fit_summary: str
    skills_matched: List[str]
    skills_missing: List[str]
    analyzed_at: Optional[datetime] = None


# Profile schemas
class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = []


class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[str] = None
    field: Optional[str] = None


class CandidateProfile(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    languages: List[str] = []
    certifications: List[str] = []


class ProfileResponse(BaseModel):
    id: UUID
    profile_json: Dict[str, Any]
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    updated_at: datetime


# Contact schemas
class ContactResponse(BaseModel):
    id: UUID
    company_id: UUID
    email: str
    name: Optional[str] = None
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    verification_status: Optional[str] = None
    verified_at: Optional[datetime] = None
    source: Optional[str] = None
    created_at: datetime


# Email schemas
class DraftEmailRequest(BaseModel):
    contact_id: Optional[UUID] = None


class DraftEmailResponse(BaseModel):
    id: Optional[UUID] = None
    subject: str
    body: str
    contact: Optional[ContactResponse] = None


# Application schemas
class ApplicationResponse(BaseModel):
    id: UUID
    job_id: UUID
    applied_at: datetime
    method: Optional[str] = None
    status: str
    notes: Optional[str] = None
