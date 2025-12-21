# Environment Variables Setup

## Overview

**Good news!** You only need **one `.env` file** at the project root. Both the Python backend and Next.js frontend will automatically load from it.

## Single Root `.env` File

Create a `.env` file in the **project root** (same directory as `python-agents/` and `nextjs-app/`):

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# SerpAPI Configuration
SERPAPI_API_KEY=your_serpapi_api_key

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# FastAPI Backend URL (for Next.js)
FASTAPI_URL=http://localhost:8000
```

## How It Works

### Python Backend
- Automatically loads from root `.env` file
- Falls back to `python-agents/.env` if you want local overrides
- Priority: `python-agents/.env` > root `.env`

### Next.js Frontend
- Automatically loads from root `.env` file via `next.config.ts`
- Falls back to `nextjs-app/.env.local` if you want local overrides
- Priority: `nextjs-app/.env.local` > root `.env.local` > root `.env`

## Optional: Local Overrides

If you need different values for local development:

1. **Python**: Create `python-agents/.env` (takes precedence over root `.env`)
2. **Next.js**: Create `nextjs-app/.env.local` (takes precedence over root `.env`)

But for most cases, just use the single root `.env` file!

## Quick Setup

1. Copy `.env.example` to `.env` in the project root
2. Fill in your API keys and credentials
3. That's it! Both Python and Next.js will use it automatically.

## Security Note

The API routes use `SUPABASE_URL` and `SUPABASE_KEY` (not `NEXT_PUBLIC_*`) because:
- These are **server-side only** variables
- They're not exposed to the browser
- This is more secure than using `NEXT_PUBLIC_*` variables

