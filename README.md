<p align="center">
  <h1 align="center">QuerySense</h1>
  <p align="center">
    <strong>Slow Query Detective Agent</strong> — AI-powered MongoDB performance optimization
  </p>
  <p align="center">
    <a href="#agent-pipeline">Pipeline</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-reference">API</a> •
    <a href="#license">License</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat&logo=google&logoColor=white" alt="Gemini">
    <img src="https://img.shields.io/badge/MongoDB_Atlas-47A248?style=flat&logo=mongodb&logoColor=white" alt="MongoDB">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs&logoColor=white" alt="Next.js">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat" alt="MIT License">
  </p>
</p>

---

## What is QuerySense?

QuerySense is a **multi-step autonomous agent** that automatically detects, diagnoses, and fixes slow MongoDB queries — built for the [Google Cloud Rapid Agent Hackathon 2026](https://rapid-agent.devpost.com) (MongoDB Track).

**This is not a chatbot.** It's an intelligent agent with a 4-step pipeline and human-in-the-loop capabilities.

### Key Features

- **Auto-Detection** — Polls MongoDB profiler for queries exceeding 100ms
- **AI Diagnosis** — Gemini 2.5 Flash analyzes root cause with confidence scoring
- **Smart Recommendations** — Generates ready-to-use `createIndex()` commands with estimated improvement
- **Self-Learning** — Stores every resolved case as embeddings via Atlas Vector Search, getting smarter over time

---

## Agent Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        QuerySense Pipeline                         │
└─────────────────────────────────────────────────────────────────────┘

  Slow Query (>100ms)
       │
       ▼
  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
  │  INTERCEPT   │────▶│   DIAGNOSE   │────▶│  RECOMMEND  │────▶│ STORE & LEARN│
  │             │     │              │     │             │     │              │
  │ Poll profiler│     │ Gemini AI +  │     │ Generate    │     │ Save pattern │
  │ Filter >100ms│     │ Vector Search│     │ createIndex │     │ + embedding  │
  │ Extract info │     │ Past cases   │     │ Est. improve│     │ Update freq  │
  └─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
       │                     │                    │                    │
       ▼                     ▼                    ▼                    ▼
   query_logs          root_cause +         Index command +      Knowledge base
   collection          confidence           improvement %        grows smarter
```

| Step | Module | What it does |
|:---:|---|---|
| 1 | `interceptor.py` | Polls `db.system.profile`, filters queries >100ms, extracts metadata |
| 2 | `diagnose.py` | Searches similar past cases via Vector Search, sends to Gemini for analysis |
| 3 | `recommender.py` | Generates `createIndex()` command with estimated improvement percentage |
| 4 | `store.py` | Saves pattern + embedding to Atlas, knowledge base learns from every case |

---

## Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **AI / LLM** | Gemini 2.5 Flash | via Google AI Studio (`google-generativeai`) |
| **Embeddings** | `gemini-embedding-001` | 3072 dimensions, cosine similarity |
| **Database** | MongoDB Atlas M0 | Vector Search + profiler data |
| **Backend** | Python + FastAPI | Async with Motor driver |
| **Frontend** | Next.js + shadcn/ui | Tailwind CSS, responsive |
| **Deploy** | Railway + Vercel | Free tier, no credit card needed |

---

## Project Structure

```
querysense/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── agent/
│   │   ├── orchestrator.py        # 4-step pipeline orchestrator
│   │   ├── interceptor.py         # MongoDB profiler poller
│   │   ├── parser.py              # Query log parser
│   │   ├── diagnose.py            # Gemini AI diagnosis
│   │   ├── recommender.py         # Index recommendation engine
│   │   └── store.py               # Pattern storage + embeddings
│   ├── db/
│   │   ├── atlas.py               # MongoDB Atlas connection
│   │   └── vector_search.py       # $vectorSearch aggregation
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Dashboard — slow query list
│   │   ├── diagnosis/[id]/        # Diagnosis detail page
│   │   └── knowledge/             # Knowledge base page
│   ├── components/
│   │   ├── QueryTable.tsx
│   │   ├── DiagnosisPanel.tsx
│   │   └── MetricCards.tsx
│   └── package.json
├── scripts/
│   ├── seed_demo_data.py          # Generate demo slow query data
│   ├── test_gemini.py             # Test Gemini API connection
│   ├── test_atlas_connection.py   # Test MongoDB Atlas connection
│   └── test_vector_search.py      # Test Vector Search pipeline
├── LICENSE
└── README.md
```

---

## Quick Start

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| MongoDB Atlas | Free tier (M0) |
| Google AI Studio | API key ([get one here](https://aistudio.google.com)) |

### 1. Clone & Setup Backend

```bash
git clone https://github.com/adindamochamad/QuerySense.git
cd QuerySense/backend

python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/querysense
MONGODB_DB=querysense
```

### 3. Verify Connections

```bash
python ../scripts/test_gemini.py           # Test Gemini API
python ../scripts/test_atlas_connection.py # Test MongoDB Atlas
python ../scripts/test_vector_search.py    # Test Vector Search
```

### 4. Seed Demo Data & Run

```bash
python ../scripts/seed_demo_data.py        # Insert 20 sample slow queries
uvicorn main:app --reload                  # Start backend at localhost:8000
```

### 5. Setup Frontend

```bash
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local → set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                                # Start frontend at localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|:---:|---|---|
| `POST` | `/analyze` | Trigger AI analysis on a slow query |
| `GET` | `/history` | List all detected query logs with status |
| `GET` | `/diagnosis/{id}` | Get detailed diagnosis for a specific query |
| `GET` | `/knowledge` | Browse the learned knowledge base |
| `GET` | `/search?q=` | Search patterns via Atlas Full Text Search |
| `POST` | `/apply-index/{id}` | Apply recommended index (human-in-the-loop) |
| `GET` | `/metrics` | Dashboard stats: detected, improved, learned |

> Interactive API docs available at `http://localhost:8000/docs` (Swagger UI)

---

## MongoDB Collections

### `query_logs` — Detected slow queries

```json
{
  "_id": "ObjectId",
  "ns": "querysense.orders",
  "query": { "status": "pending", "user_id": 123 },
  "sort": { "created_at": -1 },
  "millis": 2340,
  "plan_summary": "COLLSCAN",
  "status": "detected | analyzing | resolved",
  "created_at": "ISODate"
}
```

### `patterns` — Learned knowledge base (with vector embeddings)

```json
{
  "_id": "ObjectId",
  "query_text": "filter by status + sort by created_at on orders",
  "embedding": [0.123, 0.456, "... 3072 dimensions"],
  "root_cause": "Missing compound index on {status, created_at}",
  "index_suggestion": { "status": 1, "created_at": -1 },
  "collection_name": "orders",
  "estimated_improvement": "85%",
  "actual_improvement_ms": 2100,
  "frequency": 3,
  "resolved_at": "ISODate"
}
```

---

## How It Works

```
     User's MongoDB Database
              │
              ▼
   ┌─────────────────────┐
   │   system.profile     │   Slow queries > 100ms
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  QuerySense Agent    │
   │                     │
   │  1. Intercept query │
   │  2. Search similar  │──── Atlas Vector Search ($vectorSearch)
   │     past cases      │     gemini-embedding-001 (3072 dim)
   │  3. Diagnose with   │──── Gemini 2.5 Flash
   │     AI + context    │
   │  4. Recommend index │
   │  5. Store & learn   │──── MongoDB Atlas (patterns collection)
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │   Dashboard (UI)     │   View diagnosis, apply fix, track progress
   └─────────────────────┘
```

---

## Hackathon

Built for the **Google Cloud Rapid Agent Hackathon 2026** — MongoDB Partner Track.

| Requirement | Status |
|---|:---:|
| Uses Gemini (Google AI) | ✅ |
| Uses MongoDB meaningfully | ✅ |
| Google Cloud Agent Builder | 🔜 |
| No non-Google AI tools | ✅ |
| New project (May–June 2026) | ✅ |
| Public repo + MIT License | ✅ |
| Hosted URL for judges | 🔜 |
| 3-min video demo (English) | 🔜 |

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ☕ for the Google Cloud Rapid Agent Hackathon 2026
</p>
