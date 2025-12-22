# Multi-Agent Content Pipeline

A LangGraph-powered multi-agent system for generating high-quality blog posts from Product Requirements Documents (PRDs). Features automated research, writing, fact-checking, and style polishing with a beautiful timeline visualization.

## ✨ Features

- 🔍 **Research Agent**: Automated web research using SerpAPI
- ✍️ **Writer Agent**: Generates blog post drafts from PRDs
- ✅ **Fact-Checker Agent**: Verifies claims and loops back for corrections
- ✨ **Polisher Agent**: Refines content for style and quality
- 📊 **Supabase Logging**: Tracks all agent executions and metrics
- 🔄 **LangGraph Workflow**: Orchestrates multi-agent pipeline with conditional routing
- 📈 **Timeline Visualization**: Beautiful UI to view the complete generation process

## 🏗️ Architecture

- **Frontend**: Next.js 16 (TypeScript/React) with Tailwind CSS
- **Backend**: FastAPI (Python) with async support
- **Workflow**: LangGraph for multi-agent orchestration
- **Database**: Supabase (PostgreSQL) for logging and storage
- **Research**: SerpAPI for web search
- **LLM**: OpenAI GPT models

## 📁 Project Structure

```
multi-agent-content-pipeline/
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Example environment file
├── python-agents/          # Python backend
│   ├── agents/             # Agent implementations
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   ├── fact_checker.py
│   │   └── polisher.py
│   ├── migrations/        # Database migration SQL files
│   ├── main.py            # FastAPI server
│   ├── graph.py           # LangGraph workflow
│   ├── load_env.py        # Environment loader
│   ├── requirements.txt   # Python dependencies
│   └── test_workflow.py   # Test script
├── nextjs-app/            # Next.js frontend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── generate/    # Generate page
│   │   ├── posts/       # Posts list page
│   │   └── timeline/    # Timeline visualization
│   └── package.json
└── README.md
```

## 🚀 Quick Start (for people cloning this repo)

**New to the project?** Check out [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide!

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **SerpAPI key** ([Get one here](https://serpapi.com/dashboard))
- **Supabase account** ([Free tier works](https://supabase.com))

### Automated Setup

Run the setup script for a guided setup:

```bash
chmod +x SETUP.sh
./SETUP.sh
```

### Manual Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/HampusRydin/multi-agent-content-pipeline.git
cd multi-agent-content-pipeline
```

### Step 2: Set Up Environment Variables (You MUST use your own keys)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in **your own** API keys and URLs (do not reuse someone else’s keys):
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_service_role_key
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   LLM_MODEL=gpt-4o-mini
   LLM_TEMPERATURE=0.7
   FASTAPI_URL=http://localhost:8000
   ```

**Important:**
- You **must create your own**:
  - Supabase project
  - OpenAI API key
  - SerpAPI key
- Do **not** hardcode or reuse someone else’s credentials.
- Both Python and Next.js automatically load from this single root `.env` file.

### Can I just click the deployed URL and use it?

- If the repository owner has a public deployment (for example:  
  `https://multi-agent-content-pipeline.vercel.app` with backend  
  `https://multi-agent-pipeline-api.fly.dev`), you can **view** it as a demo.
- However, for real usage you should:
  1. **Clone this repo**
  2. Create your **own** Supabase / OpenAI / SerpAPI accounts
  3. Set your own API keys in `.env`
  4. Optionally deploy your own copies to Vercel and Fly.io

This keeps credentials private and avoids all traffic going through the author’s accounts.

### Step 3: Set Up Supabase Database

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** in your Supabase Dashboard
3. Run these migration files **in order**:
   - `python-agents/migrations/001_create_agent_logs.sql`
   - `python-agents/migrations/002_create_posts.sql`
   - `python-agents/migrations/003_add_post_id_to_agent_logs.sql`

4. Verify tables were created in **Table Editor**

**Alternative:** Run the setup script for instructions:
```bash
cd python-agents
python setup_database.py
```

### Step 4: Install Python Dependencies

```bash
cd python-agents

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Install Next.js Dependencies

```bash
cd ../nextjs-app
npm install
```

### Step 6: Start the Application

**Terminal 1 - Start Python Backend:**
```bash
cd python-agents
source venv/bin/activate
python main.py
```

You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Start Next.js Frontend:**
```bash
cd nextjs-app
npm run dev
```

You should see: `Ready - started server on 0.0.0.0:3000`

### Step 7: Use the Application

1. Open [http://localhost:3000](http://localhost:3000)
2. Click **"Generate Content"**
3. Enter your PRD and topic
4. Click **"Generate Blog Post"**
5. Wait for generation (2-5 minutes)
6. View the timeline to see the complete process!

## 🔄 Workflow

The pipeline follows this flow:

```
PRD → Researcher → Writer → Fact-Checker → (pass: Polisher, fail: Writer) → Final Blog Post
```

1. **Researcher**: Uses SerpAPI to research the topic and gather information
2. **Writer**: Creates blog post draft from PRD and research data
3. **Fact-Checker**: Verifies claims against research (loops back to writer if fails, max 3 iterations)
4. **Polisher**: Refines and polishes the final content for publication

## 📊 Database Schema

### `agent_logs` Table
- `id` (BIGSERIAL, PRIMARY KEY)
- `agent` (TEXT) - Agent name (researcher, writer, fact_checker, polisher)
- `input` (TEXT) - Agent input
- `output` (TEXT) - Agent output
- `timestamp` (TIMESTAMPTZ) - When the log was created
- `metadata` (JSONB) - Additional metrics and data
- `post_id` (BIGINT) - Links logs to posts

### `posts` Table
- `id` (BIGSERIAL, PRIMARY KEY)
- `prd` (TEXT) - Product Requirements Document
- `final_post` (TEXT) - Final polished blog post

## 🧪 Testing

Test the workflow programmatically:

```bash
cd python-agents
source venv/bin/activate
python test_workflow.py
```

Or use the helper script:
```bash
./run_test.sh
```

## 🔌 API Endpoints

### FastAPI Backend (`http://localhost:8000`)

- `GET /` - API info
- `GET /health` - Health check
- `POST /generate` - Generate blog post
  ```json
  {
    "prd": "Product Requirements Document...",
    "topic": "Blog post topic",
    "target_length": 1000,
    "style": "professional"
  }
  ```

### Next.js API Routes (`http://localhost:3000/api`)

- `GET /api/posts` - List all posts
- `GET /api/timeline/[postId]` - Get timeline for a post
- `POST /api/generate` - Generate content (proxies to FastAPI)

## 🎨 Frontend Pages

- `/` - Home page with navigation
- `/generate` - Generate new blog post form
- `/posts` - List all generated posts
- `/timeline/[postId]` - Visual timeline of generation process

## 🛠️ Troubleshooting

### Database Issues

**No entries in `posts` table:**
- Check RLS policies in Supabase Dashboard → Table Editor → Policies
- Ensure INSERT policy allows your service role key
- Or temporarily disable RLS for testing

**Agent logs not appearing in timeline:**
- Verify `post_id` column exists: Run `python verify_migration.py`
- Check that logs have `post_id` set: Run `python check_logs.py`
- Ensure you're viewing a post created after running migration 003

### API Issues

**401 Unauthorized from SerpAPI:**
- Verify your `SERPAPI_API_KEY` is correct in `.env`
- Check your SerpAPI account has credits

**OpenAI errors:**
- Verify `OPENAI_API_KEY` is correct
- Check you have sufficient API credits
- Verify `LLM_MODEL` is a valid model name

**FastAPI server not starting:**
- Ensure virtual environment is activated
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists in project root

**Next.js can't connect to FastAPI:**
- Ensure FastAPI server is running on port 8000
- Check `FASTAPI_URL` in `.env` matches your FastAPI server URL
- Verify CORS is enabled in FastAPI (it is by default)

### Workflow Issues

**Content too short:**
- Increase `target_length` parameter
- Check writer agent is receiving proper PRD

**Fact-checker always fails:**
- May indicate insufficient research data
- Check SerpAPI is returning results
- Review fact-checker logs in Supabase

**Infinite loops:**
- The fact-checker has a max iteration limit (3) to prevent infinite loops
- After 3 failures, workflow proceeds to polish anyway

## 📝 Development

### Project Scripts

**Python:**
- `python main.py` - Start FastAPI server
- `python test_workflow.py` - Test workflow
- `python setup_database.py` - Database setup helper
- `python check_logs.py` - Debug agent logs
- `python verify_migration.py` - Verify migrations

**Next.js:**
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server

### Code Structure

- **Agents** (`python-agents/agents/`): Each agent is a class with `run()` and `run_async()` methods
- **Workflow** (`python-agents/graph.py`): Defines the LangGraph workflow and state
- **API** (`python-agents/main.py`): FastAPI endpoints
- **Frontend** (`nextjs-app/app/`): Next.js App Router pages and API routes

## 🔒 Security Notes

- **Never commit `.env` files** - They're in `.gitignore`
- Use your own Supabase project - don't share credentials
- For production, adjust RLS policies in Supabase
- Consider using service role key for backend, anon key for frontend
- Rotate API keys if they were ever exposed

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 🚀 Deployment

The application is configured for deployment to:
- **Frontend** (example): `https://multi-agent-content-pipeline.vercel.app` (Vercel, Next.js)
- **Backend** (example): `https://multi-agent-pipeline-api.fly.dev` (Fly.io, FastAPI)

You should **replace these with your own domains** when you deploy, but the steps are:

- **Vercel (frontend)**  
  - Connect this GitHub repo and use `nextjs-app/` as the project root  
  - Set these environment variables in Vercel (Production):
    - `FASTAPI_URL=https://your-fly-backend-url.fly.dev`
    - `SUPABASE_URL=https://your-project-id.supabase.co`
    - `SUPABASE_KEY=your_supabase_service_role_key` (secret; server-side only)
    - `NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co`
    - `NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_or_publishable_key`

- **Fly.io (backend)**  
  - Use `python-agents/` as the app root with the included `Dockerfile` and `fly.toml`  
  - Set these secrets with `flyctl secrets set`:
    - `SUPABASE_URL=https://your-project-id.supabase.co`
    - `SUPABASE_KEY=your_supabase_service_role_key`
    - `OPENAI_API_KEY=your_openai_api_key`
    - `SERPAPI_API_KEY=your_serpapi_api_key`
    - `LLM_MODEL=gpt-4o-mini`
    - `LLM_TEMPERATURE=0.7`
    - `ENVIRONMENT=production`

Essential configuration files are included; you mainly need to:
1. Create your own Supabase project and run the migrations  
2. Deploy the backend to Fly.io and note its URL  
3. Deploy the frontend to Vercel and point `FASTAPI_URL` at your Fly.io URL  

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase Documentation](https://supabase.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Vercel Documentation](https://vercel.com/docs)
