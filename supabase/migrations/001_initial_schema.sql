-- Migration: 001_initial_schema
-- Description: Initial database schema for Jarvis Job Hunter

-- Companies discovered from job postings
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    website_url TEXT,
    is_enisa_certified BOOLEAN DEFAULT FALSE,
    is_startup_law BOOLEAN DEFAULT FALSE,
    funding_stage TEXT,
    enriched_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs from TheirStack/SerpApi
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT UNIQUE,
    source TEXT NOT NULL,
    company_id UUID REFERENCES companies(id),
    title TEXT NOT NULL,
    description TEXT,
    location TEXT,
    application_url TEXT,
    ats_type TEXT,
    posted_at TIMESTAMPTZ,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'new'
);

-- AI Analysis Results
CREATE TABLE job_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) UNIQUE,
    fit_score INTEGER CHECK (fit_score >= 0 AND fit_score <= 100),
    spanish_required BOOLEAN,
    visa_status TEXT,
    fit_summary TEXT,
    skills_matched JSONB,
    skills_missing JSONB,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Verified contacts for outreach
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    email TEXT NOT NULL,
    name TEXT,
    title TEXT,
    linkedin_url TEXT,
    verification_status TEXT,
    verified_at TIMESTAMPTZ,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Candidate profile (your digitized resume)
CREATE TABLE candidate_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_json JSONB NOT NULL,
    resume_url TEXT,
    linkedin_url TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Track applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    method TEXT,
    status TEXT DEFAULT 'submitted',
    notes TEXT
);

-- Track email outreach
CREATE TABLE email_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    contact_id UUID REFERENCES contacts(id),
    subject TEXT,
    body TEXT,
    gmail_draft_id TEXT,
    status TEXT DEFAULT 'drafted',
    drafted_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ
);

-- Polling logs
CREATE TABLE polling_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    endpoint TEXT,
    status_code INTEGER,
    jobs_found INTEGER,
    polled_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_discovered ON jobs(discovered_at DESC);
CREATE INDEX idx_job_analysis_score ON job_analysis(fit_score DESC);
CREATE INDEX idx_companies_enisa ON companies(is_enisa_certified) WHERE is_enisa_certified = TRUE;
