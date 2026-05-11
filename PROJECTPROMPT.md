# Cursor AI — Project Prompt: QuerySense

## Siapa Kamu (Context untuk Cursor)

Kamu adalah senior full-stack engineer yang membantu saya membangun project **QuerySense** — sebuah AI Agent untuk Google Cloud Rapid Agent Hackathon 2026 (rapid-agent.devpost.com), MongoDB Track.

Saya adalah backend developer dengan pengalaman di PHP, Python, MySQL, dan REST API. Saya menggunakan **Cursor AI IDE** sebagai environment utama.

---

## Apa Itu QuerySense

QuerySense adalah **Slow Query Detective Agent** — AI agent yang secara otomatis:
1. **Mendeteksi** slow queries dari MongoDB profiler
2. **Mendiagnosis** root cause menggunakan Gemini AI
3. **Merekomendasikan** index yang tepat beserta estimasi improvement
4. **Menyimpan & belajar** dari setiap kasus via MongoDB Atlas Vector Search

Ini bukan chatbot — ini multi-step autonomous agent dengan human-in-the-loop.

---

## Rules Hackathon yang Wajib Diikuti

- Harus menggunakan **Gemini** (via Google AI Studio API key ATAU Vertex AI)
- Harus menggunakan **MongoDB MCP server** secara meaningful (bukan sekadar storage)
- Harus menggunakan **Google Cloud Agent Builder** (akan diaktifkan di fase akhir setelah kredit Devpost tersedia)
- Hanya boleh pakai AI tools dari Google Cloud — **DILARANG** pakai OpenAI, Anthropic, atau AI lain
- Project harus **baru** (dibuat selama hackathon period: Mei–Juni 2026)
- Repo harus **public** di GitHub dengan **MIT License** visible di About section
- Harus ada **hosted URL** yang bisa diakses judges
- Video demo **3 menit** di YouTube/Vimeo dalam Bahasa Inggris

---

## Tech Stack

| Layer | Teknologi | Alasan |
|---|---|---|
| AI / LLM | Gemini via Google AI Studio (`google-generativeai`) | Gratis, no billing required |
| Vector Embedding | `models/gemini-embedding-001` via Google AI Studio | 3072 dimensi, gratis |
| Database | MongoDB Atlas M0 (free tier) | Core partner track, Vector Search |
| Backend | Python + FastAPI | Gemini SDK paling mature di Python |
| Frontend | Next.js + shadcn/ui + Tailwind | Clean UI, judges-friendly |
| Hosting Backend | Railway.app (free tier) | Tidak butuh kartu kredit |
| Hosting Frontend | Vercel (free tier) | Deploy Next.js paling mudah |
| GCP / Agent Builder | Aktif di fase akhir setelah kredit $100 dari Devpost | Untuk compliance hackathon |

---

## Struktur Project

```
querysense/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── agent/
│   │   ├── orchestrator.py      # 4-step pipeline agent
│   │   ├── interceptor.py       # MongoDB profiler poller
│   │   ├── parser.py            # Query log parser
│   │   ├── diagnose.py          # Gemini diagnosis module
│   │   ├── recommender.py       # Index recommendation generator
│   │   └── store.py             # Save to Atlas + embedding
│   ├── db/
│   │   ├── atlas.py             # MongoDB Atlas connection
│   │   └── vector_search.py     # $vectorSearch aggregation
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Dashboard utama (slow query list)
│   │   ├── diagnosis/[id]/      # Detail diagnosis page
│   │   └── knowledge/           # Knowledge base page
│   ├── components/
│   │   ├── QueryTable.tsx
│   │   ├── DiagnosisPanel.tsx
│   │   └── MetricCards.tsx
│   └── package.json
├── scripts/
│   └── seed_demo_data.py        # Generate 20+ dummy patterns untuk demo
├── LICENSE                      # MIT License — WAJIB ADA
└── README.md
```

---

## 4-Step Agent Pipeline (Core Logic)

```
INPUT: slow query dari MongoDB profiler (>100ms)
  │
  ▼
STEP 1 — INTERCEPT
  - Poll db.system.profile setiap 10 detik
  - Filter query dengan millis > 100
  - Extract: ns, query/filter, sort, millis, planSummary
  │
  ▼
STEP 2 — DIAGNOSE (Gemini)
  - Generate embedding dari query pattern
  - Cari 3 similar past cases via Atlas $vectorSearch
  - Kirim ke Gemini: query + explain plan + similar cases
  - Output: root_cause (string), confidence (0-1)
  │
  ▼
STEP 3 — RECOMMEND
  - Generate createIndex() command yang siap dipakai
  - Estimasi improvement dalam persen
  - Format: {"collection": "orders", "index": {"status": 1, "created_at": -1}, "estimated_improvement": "85%"}
  │
  ▼
STEP 4 — STORE & LEARN
  - Simpan ke Atlas collection "patterns":
    {query_text, embedding, root_cause, index_suggestion, improvement_ms, resolved_at}
  - Knowledge base makin pintar setiap ada kasus baru

OUTPUT: diagnosis JSON + index recommendation + similar past cases
```

---

## MongoDB Collections Schema

### Collection: `query_logs`
```json
{
  "_id": "ObjectId",
  "ns": "querysense.orders",
  "query": {"status": "pending", "user_id": 123},
  "sort": {"created_at": -1},
  "millis": 2340,
  "plan_summary": "COLLSCAN",
  "status": "detected | analyzing | resolved",
  "created_at": "ISODate"
}
```

### Collection: `patterns`
```json
{
  "_id": "ObjectId",
  "query_text": "filter by status + sort by created_at on orders",
  "embedding": [0.123, 0.456, ...],
  "root_cause": "Missing compound index on {status, created_at}",
  "index_suggestion": {"status": 1, "created_at": -1},
  "collection_name": "orders",
  "estimated_improvement": "85%",
  "actual_improvement_ms": 2100,
  "frequency": 3,
  "resolved_at": "ISODate"
}
```

---

## Gemini Prompt Template (untuk diagnosa)

```python
DIAGNOSIS_PROMPT = """
You are a MongoDB performance expert. Analyze this slow query and provide diagnosis.

SLOW QUERY:
- Collection: {collection}
- Filter: {query_filter}
- Sort: {sort}
- Execution time: {millis}ms
- Plan: {plan_summary}

SIMILAR PAST CASES (from knowledge base):
{similar_cases}

Respond in JSON format:
{{
  "root_cause": "explanation of why this query is slow",
  "index_suggestion": {{"field1": 1, "field2": -1}},
  "estimated_improvement": "X%",
  "explanation": "why this index will help",
  "confidence": 0.0-1.0
}}
"""
```

---

## API Endpoints (FastAPI)

```
POST /analyze          - Trigger manual analysis pada 1 query log
GET  /history          - List semua query logs + status (polling dashboard)
GET  /diagnosis/{id}   - Detail diagnosis untuk 1 query
GET  /knowledge        - List semua patterns di knowledge base
GET  /search?q=        - Search knowledge base via Atlas Full Text Search
POST /apply-index/{id} - Apply recommended index (human-in-the-loop)
GET  /metrics          - Stats: total detected, avg improvement, patterns learned
```

---

## Frontend Pages

### 1. Dashboard Utama (`/`)
- Header metric cards: "Queries Detected", "Avg Improvement %", "Patterns Learned"
- Tabel slow queries: query text | collection | ms | status badge | action button
- Status badge: 🔴 Detected → 🟡 Analyzing → 🟢 Resolved
- Real-time polling setiap 5 detik ke GET /history
- Klik baris → navigasi ke halaman detail

### 2. Detail Diagnosis (`/diagnosis/[id]`)
- Panel kiri: raw query info (collection, filter, sort, millis, plan)
- Panel kanan: Gemini diagnosis hasil (root cause, confidence score)
- Index suggestion dengan syntax highlight + tombol "Copy" dan "Apply Index"
- Section "Similar Past Cases" — 3 kartu dari Vector Search hasil
- Tombol "Mark as Resolved" → update status ke resolved

### 3. Knowledge Base (`/knowledge`)
- Search bar → Atlas Full Text Search
- Grid kartu: query pattern | root cause | improvement | frequency
- Sorted by frequency (paling sering muncul di atas)

---

## Environment Variables

```env
# Backend (.env)
GEMINI_API_KEY=your_google_ai_studio_api_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/querysense
MONGODB_DB=querysense

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
```

---

## Sprint Timeline (Sisa Hari)

| Fase | Hari | Tanggal | Target |
|---|---|---|---|
| Setup | 1–6 | 10–15 Mei | API keys, Atlas, GitHub |
| Core Agent | 7–16 | 16–25 Mei | Full pipeline jalan |
| Backend + UI | 17–22 | 26–31 Mei | FastAPI + Next.js |
| Deploy + Submit | 23–32 | 1–10 Jun | Live URL + video + Devpost |

**Hard deadline submit: 02.00 WIB, Jumat 12 Juni 2026**

---

## Aturan Coding untuk Cursor

1. **Bahasa**: Python untuk backend, TypeScript untuk frontend
2. **Style**: Clean, readable, well-commented — judges akan lihat kodenya
3. **Error handling**: Semua API call harus ada try/except
4. **Env vars**: Semua credentials pakai .env — jangan hardcode
5. **README**: Update setiap ada modul baru selesai dibuat
6. **Commit style**: `feat: add query interceptor module` — conventional commits
7. **Jangan pakai AI selain Gemini** — rules hackathon melarang OpenAI dll

---

## Cara Mulai (Hari Ini)

Task aktif sekarang adalah **Hari 1: Aktivasi Google AI Studio API Key**

1. Buka aistudio.google.com
2. Login Google, buat API key
3. Simpan di file `.env` dengan key `GEMINI_API_KEY`
4. Test dengan script berikut:

```python
# test_gemini.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Analyze this MongoDB slow query: db.orders.find({status: 'pending'}).sort({created_at: -1}) took 2340ms. Why is it slow?")
print(response.text)
```

Jika berhasil → lanjut ke Hari 2.
