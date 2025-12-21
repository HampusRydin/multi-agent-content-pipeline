# Multi-Agent Content Pipeline

A LangGraph-powered multi-agent system for generating high-quality blog posts from Product Requirements Documents (PRDs).

## Features

- 🔍 **Research Agent**: Automated web research using SerpAPI
- ✍️ **Writer Agent**: Generates blog post drafts from PRDs
- ✅ **Fact-Checker Agent**: Verifies claims and loops back for corrections
- ✨ **Polisher Agent**: Refines content for style and quality
- 📊 **Supabase Logging**: Tracks all agent executions and metrics
- 🔄 **LangGraph Workflow**: Orchestrates multi-agent pipeline with conditional routing

## Architecture

- **Frontend**: Next.js (TypeScript/React)
- **Backend**: FastAPI (Python)
- **Workflow**: LangGraph
- **Database**: Supabase (PostgreSQL)
- **Research**: SerpAPI
- **LLM**: OpenAI

## Project Structure

```
multi-agent-content-pipeline/
├── nextjs-app/          # Next.js frontend
│   ├── app/
│   ├── components/
│   └── ...
├── python-agents/       # Python backend with agents
│   ├── agents/
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   ├── fact_checker.py
│   │   └── polisher.py
│   ├── migrations/     # Database migration files
│   ├── main.py         # FastAPI server
│   └── graph.py        # LangGraph workflow
└── README.md
```

## Prerequisites

- Python 3.9+ 
- Node.js 18+ and npm
- OpenAI API key
- SerpAPI key (for research functionality)
- Supabase account (free tier works)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/HampusRydin/multi-agent-content-pipeline.git
cd multi-agent-content-pipeline
```

### 2. Set Up Python Backend

```bash
cd python-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install manually:
pip install fastapi uvicorn langgraph openai supabase serpapi python-dotenv
```

### 3. Set Up Supabase Database

**Important**: Create your own Supabase project at https://supabase.com

1. Create a new Supabase project
2. Go to **SQL Editor** in your Supabase Dashboard
3. Run the migration files in order:
   - `python-agents/migrations/001_create_agent_logs.sql`
   - `python-agents/migrations/002_create_posts.sql`
4. Or run the setup script:
   ```bash
   python setup_database.py
   ```

### 4. Configure Environment Variables

**Create a single `.env` file at the project root** (same directory as `python-agents/` and `nextjs-app/`):

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key_here

# LLM Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# FastAPI Backend URL (for Next.js)
FASTAPI_URL=http://localhost:8000
```

**Note**: Both Python and Next.js will automatically load from this root `.env` file. You don't need separate `.env` files!

### 5. Set Up Next.js Frontend

```bash
cd nextjs-app

# Install dependencies
npm install
```

## Running the Application

### Start the Python Backend

```bash
cd python-agents
source venv/bin/activate
python main.py
```

The API will be available at `http://localhost:8000`

### Start the Next.js Frontend

```bash
cd nextjs-app
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Workflow

The pipeline follows this flow:

```
PRD → Researcher → Writer → Fact-Checker → (pass: Polisher, fail: Writer) → Final Blog Post
```

1. **Researcher**: Uses SerpAPI to research the topic
2. **Writer**: Creates blog post draft from PRD and research
3. **Fact-Checker**: Verifies claims against research (loops back to writer if fails)
4. **Polisher**: Refines and polishes the final content

## Testing

Run the test script to test the workflow:

```bash
cd python-agents
python test_workflow.py
```

## API Endpoints

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

## Database Tables

- **agent_logs**: Logs all agent executions with inputs, outputs, and metrics
- **posts**: Stores final blog posts with their PRDs

## Troubleshooting

### Database Issues
- **No entries in `posts` table**: Check RLS policies in Supabase. The migrations include policies, but verify they're active.
- **Agent logs not appearing**: Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set correctly in `.env`

### API Issues
- **401 Unauthorized from SerpAPI**: Verify your `SERPAPI_API_KEY` is correct
- **OpenAI errors**: Check your `OPENAI_API_KEY` and ensure you have sufficient credits
- **Fact-checker always fails**: This may indicate insufficient research data or overly strict checking

### Workflow Issues
- **Content too short**: Adjust `target_length` parameter or check writer agent prompts
- **Infinite loops**: The fact-checker has a max iteration limit (3) to prevent infinite loops

## Security Notes

- Use your own Supabase project - don't share credentials
- For production, adjust RLS policies in Supabase
- Consider using service role key for backend, anon key for frontend
- Rotate API keys if they were ever exposed

## License

MIT License - see [LICENSE](LICENSE) file for details.

