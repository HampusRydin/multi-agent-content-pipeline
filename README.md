# Multi-Agent Content Pipeline

### *Generate high-quality blog posts from PRDs using a fully orchestrated multi-agent system.*

This project turns a **Product Requirements Document (PRD)** into a polished, fact-checked, publication-ready blog post using a multi-agent workflow.

Agents and core components:

- 🧠 **Research Agent** – Uses SerpAPI for web research  
- ✍️ **Writer Agent** – Drafts the article from PRD + research  
- 🔍 **Fact-Checker Agent** – Iteratively validates claims, can loop back to writer  
- 🎨 **Polisher Agent** – Refines tone, clarity, and style  
- 🧩 **LangGraph** – Orchestrates the multi-agent workflow and loops  
- 📊 **Supabase** – Stores posts and detailed agent logs  
- 🌐 **Next.js UI** – Timeline view of the entire generation process  

Deployed as:

- **Frontend (Vercel)** → Next.js App Router  
- **Backend (Fly.io)** → FastAPI + LangGraph  
- **Database (Supabase)** → PostgreSQL for logs and posts  

---

## 🚀 Live Demo

👉 **Frontend:**  
`https://multi-agent-content-pipeline.vercel.app`

👉 **Backend (reference only):**  
`https://multi-agent-pipeline-api.fly.dev`

### 🔐 Access Notice

The live demo is **password-protected** to prevent abuse of API credits.

- Employers / reviewers: the demo password is provided in application materials or by request.  
- After login, you can:
  - Submit a PRD  
  - Watch the multi-agent pipeline run  
  - Inspect the timeline of each agent’s output  

> You do **not** need to install or run anything locally to evaluate the project.

---

## 🎯 What This Project Demonstrates (For Employers)

This repository showcases a complete, production-style AI engineering system:

- ✔ Multi-agent orchestration with LangGraph  
- ✔ End-to-end architecture (Next.js frontend + FastAPI backend)  
- ✔ Cloud-native deployment (Vercel + Fly.io + Supabase)  
- ✔ Secure secrets management and environment setup  
- ✔ Supabase integration with structured logging (`agent_logs`, `posts`)  
- ✔ Timeline UI to visualize agent steps and iterations  
- ✔ Clean, modular code structure suitable for extension  

You can:
- Use the live demo to see the workflow end-to-end  
- Browse the code to understand architecture and implementation details  

---

## ⚙️ Architecture Overview

- **Frontend:** Next.js (App Router), TypeScript, Tailwind-style utility classes  
- **Backend:** FastAPI + LangGraph (Python)  
- **Database:** Supabase (PostgreSQL)  
- **Search:** SerpAPI (for the research agent)  
- **LLM:** OpenAI GPT models (configurable via `LLM_MODEL`)  
- **Deployment:**  
  - Vercel → Next.js app (`nextjs-app/`)  
  - Fly.io → Python backend (`python-agents/`)  
  - Supabase → Hosted Postgres for logs and posts  

The UI exposes:
- `/generate` – Create a new blog post from a PRD  
- `/posts` – See all created posts  
- `/timeline/[postId]` – Step-by-step timeline of the agents for a post  

---

## 📁 Project Structure

```text
multi-agent-content-pipeline/
├── .env                 # Root env file (not committed; see .env.example)
├── .env.example         # Template for local env variables
├── python-agents/       # Backend (FastAPI + LangGraph)
│   ├── agents/          # Researcher, writer, fact_checker, polisher
│   ├── graph.py         # LangGraph workflow definition
│   ├── main.py          # FastAPI app (exposes /generate)
│   ├── migrations/      # Supabase SQL migrations (tables, columns, RLS)
│   ├── requirements.txt # Python dependencies
│   └── test_workflow.py # Local workflow test script
├── nextjs-app/          # Frontend (Next.js)
│   ├── app/             # App Router pages and API routes
│   │   ├── page.tsx             # Landing page
│   │   ├── login/page.tsx       # Demo login page
│   │   ├── generate/page.tsx    # Generate form
│   │   ├── posts/page.tsx       # Posts list
│   │   ├── timeline/[postId]/   # Timeline view
│   │   └── api/                 # Next.js API routes
│   │       ├── generate/route.ts
│   │       ├── posts/route.ts
│   │       └── timeline/[postId]/route.ts
│   ├── middleware.ts    # Protects demo with password cookie
│   └── package.json
└── README.md
```

---

## 💡 Using the Project: Demo vs. Self-Hosting

### ✔ Live Demo (Recommended for Employers)

- Open: `https://multi-agent-content-pipeline.vercel.app`  
- Enter the **demo password** on the `/login` page  
- Generate a post from a PRD and inspect the timeline  

You don’t need to:
- Clone the repo  
- Set up `.env`  
- Deploy anything  

### ✔ Self-Hosting (For Developers)

To run your **own** copy (with your own API keys and quotas):

1. **Clone the repo**
   ```bash
   git clone https://github.com/HampusRydin/multi-agent-content-pipeline.git
   cd multi-agent-content-pipeline
   ```

2. **Create your own accounts**
   - Supabase project (free tier is fine)  
   - OpenAI API key  
   - SerpAPI key  

3. **Create a root `.env` from the template**
   ```bash
   cp .env.example .env
   ```

   Fill in **your own** values:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_service_role_key
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_or_publishable_key
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_API_KEY=your_serpapi_api_key
   LLM_MODEL=gpt-4o-mini
   LLM_TEMPERATURE=0.7
   FASTAPI_URL=http://localhost:8000
   ```

4. **Run Supabase migrations**
   - In Supabase Dashboard → SQL Editor, run:
     - `python-agents/migrations/001_create_agent_logs.sql`
     - `python-agents/migrations/002_create_posts.sql`
     - `python-agents/migrations/003_add_post_id_to_agent_logs.sql`

5. **Start the backend (Python)**
   ```bash
   cd python-agents
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

6. **Start the frontend (Next.js)**
   ```bash
   cd ../nextjs-app
   npm install
   npm run dev
   ```

7. **Use it locally**
   - Frontend: `http://localhost:3000`  
   - Backend: `http://localhost:8000`  

---

## 🔐 Security Notes

- `.env` and keys are **never** committed to Git (see `.gitignore`).  
- Supabase **service role key** is used only on:
  - Backend (FastAPI on Fly.io)  
  - Next.js API routes on Vercel  
- The frontend uses `NEXT_PUBLIC_SUPABASE_KEY` (anon key) when needed.  
- Demo access is protected behind `DEMO_PASSWORD` and an HTTP-only cookie.  
- RLS is enabled on Supabase tables; policies in migrations allow basic inserts/selects and can be tightened for production.  
- You should rotate keys if they are ever exposed.  

---

## 🛠️ Developer Quick Start (Local)

Key steps:

1. Clone and create `.env` (see "Self-Hosting" section above)  
2. Run Supabase migrations  
3. Start backend: `python-agents/main.py`  
4. Start frontend: `nextjs-app` → `npm run dev`  
5. Visit `http://localhost:3000` and generate content  

To test the workflow without the UI:

```bash
cd python-agents
source venv/bin/activate
python test_workflow.py
```

---

## ☁️ Deployment Guide (Summary)

### Backend (Fly.io)

From `python-agents/`:

```bash
flyctl launch

flyctl secrets set \
  SUPABASE_URL="https://your-project.supabase.co" \
  SUPABASE_KEY="your_supabase_service_role_key" \
  OPENAI_API_KEY="your_openai_api_key" \
  SERPAPI_API_KEY="your_serpapi_api_key" \
  LLM_MODEL="gpt-4o-mini" \
  LLM_TEMPERATURE="0.7" \
  ENVIRONMENT="production"

flyctl deploy
```

Your backend will be available at:

```text
https://your-fly-app-name.fly.dev
```

### Frontend (Vercel)

When importing the repo into Vercel:

- **Root Directory**: `nextjs-app`  
- **Framework Preset**: Next.js  

Set these environment variables (Production):

```ini
FASTAPI_URL=https://your-fly-app-name.fly.dev
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_or_publishable_key
DEMO_PASSWORD=some_demo_password   # Optional: protects live demo
```

Vercel will build and deploy the frontend; the app will call your Fly.io backend.

---

## 📊 Database Schema (Supabase)

### `agent_logs`

Stores logs from every agent step in the workflow.

- `id` (BIGSERIAL, PK)  
- `agent` (TEXT) – `researcher`, `writer`, `fact_checker`, `polisher`  
- `input` (TEXT) – Agent input  
- `output` (TEXT) – Agent output  
- `timestamp` (TIMESTAMPTZ) – When the log was created  
- `metadata` (JSONB) – Timing, word counts, status, etc.  
- `post_id` (BIGINT) – Foreign-key-style link to `posts.id`  

### `posts`

Stores PRDs and final polished posts.

- `id` (BIGSERIAL, PK)  
- `prd` (TEXT) – Original PRD text  
- `final_post` (TEXT) – Final blog post after polishing  

Full definitions are in `python-agents/migrations/`.

---

## 🧭 Workflow Diagram

```text
PRD
 ↓
Research Agent
 ↓
Writer Agent
 ↓
Fact-Checker Agent (retry loop up to 3)
 ↓
Polisher Agent
 ↓
Final Post + Supabase Logs + Timeline View
```

The Fact-Checker can route back to the Writer up to a max number of iterations to improve factual accuracy.

---

## 🧪 Testing

From `python-agents/`:

```bash
source venv/bin/activate
python test_workflow.py
```

Or run:

```bash
./run_test.sh
```

This executes the LangGraph workflow end-to-end and logs results to Supabase.

---

## 📄 License

MIT License – see [`LICENSE`](LICENSE) for details.

---

## 📝 Summary for Employers

To evaluate this project:

1. Visit the live demo URL  
2. Use the provided demo password to log in  
3. Paste in a PRD and generate content  
4. Inspect the multi-agent timeline and generated post  
5. Browse this repository to review architecture, code quality, and deployment setup  

No local setup is required to see the system in action.  
