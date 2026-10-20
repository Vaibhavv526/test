# AuraMatch — Agentic AI Dating Platform

An autonomous "agentic dating" simulation demo where AI agents represent consenting individuals, simulate dating conversations on their behalf, and compute nuanced psychological compatibility scores and rankings.

---

## 🌟 Key Architecture & Highlights

- **Persona Extraction (`analyze_profile`)**: Extracts structured psychological profiles (emotional needs, core values, communication styles, hobbies, and dealbreakers) from unstructured bio text (LinkedIn "About", Instagram bio, personal notes) via **Anthropic Claude** JSON mode / forced tool calling.
- **Autonomous Date Simulation (`agent_date`)**: Prompts two independent persona agents with their respective `ProfileAnalysis`. The agents engage in multi-turn simulated banter, probing values, testing alignment, and discreetly checking dealbreakers, complete with internal agent thoughts and an overall compatibility score (0–100).
- **Compatibility Ranking (`rank_matches`)**: Evaluates and ranks candidates for any selected individual, displaying structured scores, rationale, shared strengths, and friction points.
- **Strict Data Policy (No Web Scraping)**: Uses consenting self-reported participant text or diverse synthetic personas generated via Claude / curated archetypes. Profiles are tagged with `source: "self-reported"` or `source: "synthetic"` for full transparency.
- **Modular LLM Layer (`backend/app/agent.py`)**: All LLM interactions are isolated in a single module. Provider and model are configurable via environment variables, with a smart simulation fallback if an Anthropic API key is not yet provided.

---

## 🏗️ Tech Stack

- **Frontend**: React 19, Vite, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI (Python 3.12), Pydantic v2, Uvicorn
- **Database**: SQLite locally, PostgreSQL on Neon / Render via SQLAlchemy ORM
- **LLM Provider**: Anthropic Claude API (`claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, etc.)

---

## 🚀 Local Development Quickstart

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy env example and set your Anthropic API Key
cp .env.example .env
# Edit .env with your keys:
# ANTHROPIC_API_KEY=your_key_here
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Seed 25 rich synthetic profiles out of the box
python generate_synthetic_profiles.py --seed-curated

# Run FastAPI backend locally
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be live at `http://127.0.0.1:8000`. Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Open `http://localhost:5173` in your browser. The Vite development proxy forwards `/api` requests to `http://localhost:8000`.

---

## 🌐 Deployment Guide (Render + Vercel + Neon)

### 1. Database Provisioning (Neon Postgres)
1. Create a free serverless PostgreSQL database at [Neon.tech](https://neon.tech).
2. Copy your connection string (format: `postgresql://user:password@ep-xyz.neon.tech/neondb?sslmode=require`).
3. SQLAlchemy in `backend/app/database.py` automatically normalizes legacy `postgres://` URLs to `postgresql://` and creates all required tables on startup.

---

### 2. Backend Deployment (Render Web Service)
1. Create a new **Web Service** on [Render](https://render.com) connected to your GitHub repository.
2. Configure the following settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set the **Environment Variables** in the Render Dashboard:
   | Variable | Value / Description |
   | :--- | :--- |
   | `ANTHROPIC_API_KEY` | Your Anthropic Claude API key |
   | `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` (or preferred model) |
   | `DATABASE_URL` | Your Neon PostgreSQL connection string |
   | `ALLOWED_ORIGINS` | Comma-separated allowed frontend origins (e.g. `https://your-auramatch.vercel.app,http://localhost:5173`) |
4. Deploy the service. Note your public backend URL (e.g. `https://auramatch-api.onrender.com`).

---

### 3. Frontend Deployment (Vercel)
1. Import your GitHub repository on [Vercel](https://vercel.com).
2. Configure project settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add the **Environment Variable** in Vercel:
   | Variable | Value / Description |
   | :--- | :--- |
   | `VITE_API_URL` | Your Render backend URL (e.g. `https://auramatch-api.onrender.com`) |
4. Deploy. Once deployed, add your Vercel domain to the `ALLOWED_ORIGINS` variable on Render.

---

## 🔄 How to Swap in Real Self-Reported Participant Data

1. **Intake Page / API**:
   - Participants paste their own LinkedIn "About" section, Instagram bio, or free-form notes directly into the **Intake & Seed** page.
   - Or make an HTTP `POST /api/profiles/intake` request with:
     ```json
     {
       "name": "Jordan Rivera",
       "raw_input": "Full bio text from opt-in participant...",
       "source": "self-reported"
     }
     ```
   - Claude automatically analyzes the text and creates their autonomous agent.
2. **Filtering & Auditability**:
   - Every profile card and database record explicitly retains `source: "self-reported"` vs `source: "synthetic"`.
   - The Candidate Directory allows filtering by source with one click.
3. **Database Upgrade to PostgreSQL**:
   - Set `DATABASE_URL` in your environment:
     ```env
     DATABASE_URL=postgresql://user:password@localhost:5432/agentic_dating
     ```
   - SQLAlchemy automatically initializes the schema with full Postgres compatibility.

---

## 🧠 LLM Architecture (`agent.py`)

All LLM calls are confined to `backend/app/agent.py`:
- `analyze_profile(raw_text, fallback_name)`: Uses Anthropic's tool calling schema to enforce `ProfileAnalysis` JSON output.
- `agent_date(profile_a, profile_b, id_a, id_b)`: Creates a simulated dialogue with inner thoughts and compatibility scores.
- `generate_synthetic_profiles(count)`: Generates diverse fictional personas across professions, ages, and values.

---

## 📂 Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, lifespan & CORS
│   │   ├── models.py            # Pydantic schemas (ProfileAnalysis, DateTranscript)
│   │   ├── database.py          # SQLAlchemy SQLite / Postgres configuration
│   │   ├── agent.py             # Single module for all Anthropic Claude LLM calls
│   │   ├── seed_data.py         # 25 pre-curated realistic synthetic profiles
│   │   └── api/
│   │       ├── profiles.py      # Intake, listing, deletion
│   │       ├── dates.py         # Date simulation & transcript replay
│   │       └── rankings.py      # Compatibility ranking algorithm
│   ├── generate_synthetic_profiles.py # CLI seed & generator script
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/Navbar.jsx
│   │   ├── pages/
│   │   │   ├── IntakePage.jsx
│   │   │   ├── ProfilesPage.jsx
│   │   │   ├── DateSimulatorPage.jsx
│   │   │   └── RankingsPage.jsx
│   │   ├── services/api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```
