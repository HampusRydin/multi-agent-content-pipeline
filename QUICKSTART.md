# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- API keys: OpenAI, SerpAPI, Supabase

## Setup Steps

### 1. Clone and Setup

```bash
git clone https://github.com/HampusRydin/multi-agent-content-pipeline.git
cd multi-agent-content-pipeline

# Run the setup script
chmod +x SETUP.sh
./SETUP.sh
```

Or manually:

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
# Then continue with steps below...
```

### 2. Configure Environment

Edit `.env` in the project root and add:
- `SUPABASE_URL` - From Supabase Dashboard → Settings → API
- `SUPABASE_KEY` - Service role key from Supabase
- `OPENAI_API_KEY` - From OpenAI platform
- `SERPAPI_API_KEY` - From SerpAPI dashboard

### 3. Set Up Database

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project (or use existing)
3. Go to **SQL Editor**
4. Run these files **in order**:
   - `python-agents/migrations/001_create_agent_logs.sql`
   - `python-agents/migrations/002_create_posts.sql`
   - `python-agents/migrations/003_add_post_id_to_agent_logs.sql`

### 4. Start Backend

```bash
cd python-agents
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

Should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

### 5. Start Frontend

In a **new terminal**:

```bash
cd nextjs-app
npm run dev
```

Should see: `Ready - started server on 0.0.0.0:3000`

### 6. Use It!

1. Open [http://localhost:3000](http://localhost:3000)
2. Click **"Generate Content"**
3. Enter PRD and topic
4. Click **"Generate Blog Post"**
5. Wait 2-5 minutes
6. View the timeline!

## Troubleshooting

**Backend won't start:**
- Check virtual environment is activated
- Verify `.env` file exists in project root
- Check all dependencies installed: `pip install -r requirements.txt`

**Frontend won't start:**
- Check Node.js version: `node --version` (needs 18+)
- Try deleting `node_modules` and running `npm install` again

**No logs in timeline:**
- Verify migration 003 was run (adds `post_id` column)
- Check that you're viewing a post created after running all migrations
- Run `python check_logs.py` to debug

**API errors:**
- Verify all API keys in `.env` are correct
- Check Supabase RLS policies allow INSERT/SELECT
- Ensure FastAPI server is running on port 8000

## Need Help?

See the full [README.md](README.md) for detailed documentation.

