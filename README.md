# QuerySense — Slow Query Detective Agent

> AI Agent yang secara otomatis mendeteksi, mendiagnosis, dan merekomendasikan solusi untuk MongoDB slow queries.

Built for **Google Cloud Rapid Agent Hackathon 2026** — MongoDB Track.

## What is QuerySense?

QuerySense is a **multi-step autonomous agent** that:
1. **Intercepts** slow queries from MongoDB profiler (>100ms)
2. **Diagnoses** root cause using Gemini AI
3. **Recommends** optimal indexes with estimated improvement
4. **Learns** from every resolved case via MongoDB Atlas Vector Search

This is not a chatbot — it's an intelligent agent with human-in-the-loop capabilities.

## Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Gemini 2.0 Flash via Google AI Studio |
| Vector Embedding | text-embedding-004 (768 dimensions) |
| Database | MongoDB Atlas (Vector Search) |
| Backend | Python + FastAPI |
| Frontend | Next.js + shadcn/ui + Tailwind CSS |
| Hosting | Railway (backend) + Vercel (frontend) |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier M0)
- Google AI Studio API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # atau venv\Scripts\activate di Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan API keys kamu
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local dengan backend URL
npm run dev
```

### Test Gemini Connection

```bash
python scripts/test_gemini.py
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /analyze | Trigger manual analysis |
| GET | /history | List all query logs |
| GET | /diagnosis/{id} | Diagnosis detail |
| GET | /knowledge | Knowledge base patterns |
| GET | /search?q= | Search knowledge base |
| POST | /apply-index/{id} | Apply recommended index |
| GET | /metrics | Dashboard statistics |

## Agent Pipeline

```
Slow Query (>100ms) → Intercept → Diagnose (Gemini) → Recommend Index → Store & Learn
```

## License

MIT License — see [LICENSE](LICENSE) file.
