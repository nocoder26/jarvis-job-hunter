# Jarvis Job Hunter

Automated job sourcing and application engine for frontier tech roles in Spain, with HQP Visa/Startup Law company identification and 1-click cold outreach.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              NETLIFY                                     │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     Next.js Dashboard (apps/web)                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              RENDER                                      │
│  ┌────────────────────────┐     ┌────────────────────────────────────┐ │
│  │   FastAPI Backend      │     │   Background Worker                 │ │
│  │   (apps/api)           │     │   (apps/worker)                     │ │
│  └────────────────────────┘     └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            SUPABASE                                      │
│           PostgreSQL  │  Storage  │  Edge Functions                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
jarvis-job-hunter/
├── apps/
│   ├── web/          # Next.js frontend (Netlify)
│   ├── api/          # FastAPI backend (Render)
│   └── worker/       # Background jobs (Render)
├── packages/
│   └── shared/       # Shared types/utilities
├── supabase/
│   └── migrations/   # Database migrations
└── .github/
    └── workflows/    # CI/CD
```

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Supabase account
- API keys for: TheirStack, SerpApi, Gemini, Apollo, ZeroBounce, Proxycurl

### Local Development

1. **Frontend (apps/web)**
```bash
cd apps/web
npm install
npm run dev
```

2. **Backend (apps/api)**
```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. **Worker (apps/worker)**
```bash
cd apps/worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Environment Variables

See `.env.example` files in each app directory.

## Features

- **Context Engine**: Resume parsing, LinkedIn enrichment, profile generation
- **Hunter Engine**: Job polling from TheirStack/SerpApi, company enrichment
- **Brain Engine**: AI-powered job analysis, contact discovery, email validation
- **Action Engine**: Dashboard UI, auto-apply, email drafting

## License

MIT
