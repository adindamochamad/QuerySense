# QuerySense — Sprint Timeline Detail

**Hard Deadline: 02.00 WIB, Jumat 12 Juni 2026**

---

## Fase 1: Setup (Hari 1–6 | 10–15 Mei)

### ✅ Hari 1 — Aktivasi Gemini API (10 Mei)
- [x] Buat API key di aistudio.google.com
- [x] Simpan di `backend/.env`
- [x] Test koneksi dengan `scripts/test_gemini.py`
- [x] Model yang dipakai: `gemini-2.5-flash`

### ✅ Hari 2 — Setup MongoDB Atlas (11 Mei)
- [x] Buat cluster M0 (free tier) di cloud.mongodb.com
- [x] Buat database user + whitelist IP
- [x] Buat database `querysense`
- [x] Buat collections: `query_logs`, `patterns`
- [x] Update `MONGODB_URI` di `backend/.env`
- [x] Test koneksi dari Python (`scripts/test_atlas_connection.py`)
- [x] Jalankan `scripts/seed_demo_data.py` (20 query logs inserted)

### ✅ Hari 3 — Setup Atlas Vector Search Index (12 Mei)
- [x] Buat Vector Search index di collection `patterns`
  - Index name: `vector_index`
  - Field: `embedding` (3072 dimensi, cosine similarity)
  - ⚠️ Model diubah: `text-embedding-004` → `gemini-embedding-001` (768→3072 dim)
- [x] Test embedding dengan `gemini-embedding-001` (3072 dimensi, berhasil)
- [x] Test $vectorSearch aggregation pipeline (score tertinggi: 0.9745)
- [x] Update model embedding di `backend/db/vector_search.py` dan `backend/agent/store.py`
- [x] Buat script `scripts/test_vector_search.py` — test lengkap index + embedding + search

### ✅ Hari 4 — GitHub Repo + CI Setup (11 Mei — lebih cepat dari jadwal)
- [x] Init git repo
- [x] Buat GitHub repo public: `adindamochamad/QuerySense`
- [x] Push initial commit (28 files, 1790 insertions)
- [x] MIT License terlihat di About section (terverifikasi)
- [x] Setup .gitignore (`.env` aman, tidak ter-push)
- [x] Tambah topics: mongodb, gemini-ai, slow-query, vector-search, fastapi, hackathon, ai-agent

### ⬜ Hari 5–6 — Project Structure Finalisasi (14–15 Mei)
- [ ] Review semua module placeholder
- [ ] Pastikan import path benar
- [ ] Test `uvicorn main:app --reload` bisa jalan
- [ ] Buat script `test_atlas_connection.py`

---

## Fase 2: Core Agent (Hari 7–16 | 16–25 Mei)

### ⬜ Hari 7–8 — Interceptor Module (16–17 Mei)
- [ ] Implementasi polling `db.system.profile`
- [ ] Filter query > 100ms
- [ ] Extract: ns, command/filter, sort, millis, planSummary
- [ ] Simpan ke collection `query_logs` dengan status "detected"
- [ ] Test dengan dummy profiler data

### ⬜ Hari 9–10 — Parser + Embedding Module (18–19 Mei)
- [ ] Finalisasi `parser.py` — parse raw profiler output
- [ ] Implementasi embedding generation (`text-embedding-004`)
- [ ] Test embedding output (harus 768 dimensi)
- [ ] Simpan embedding ke collection `patterns`

### ⬜ Hari 11–13 — Diagnose Module + Gemini Integration (20–22 Mei)
- [ ] Finalisasi prompt template untuk diagnosis
- [ ] Implementasi Vector Search untuk cari similar cases
- [ ] Kirim ke Gemini: query + plan + similar cases
- [ ] Parse JSON response dari Gemini
- [ ] Handle error/fallback kalau response bukan JSON
- [ ] Test end-to-end: input slow query → output diagnosis

### ⬜ Hari 14–15 — Recommender + Store Module (23–24 Mei)
- [ ] Generate `createIndex()` command dari diagnosis
- [ ] Hitung estimasi improvement percentage
- [ ] Simpan pattern baru ke `patterns` collection + embedding
- [ ] Update frequency kalau pattern sudah ada
- [ ] Test knowledge base growing

### ⬜ Hari 16 — Orchestrator Integration Test (25 Mei)
- [ ] Hubungkan semua 4 step dalam orchestrator
- [ ] Test full pipeline: intercept → diagnose → recommend → store
- [ ] Fix bugs dari integration
- [ ] Pastikan status update: detected → analyzing → resolved

---

## Fase 3: Backend API + Frontend UI (Hari 17–22 | 26–31 Mei)

### ⬜ Hari 17–18 — FastAPI Endpoints (26–27 Mei)
- [ ] `POST /analyze` — trigger manual analysis
- [ ] `GET /history` — list semua query logs + status
- [ ] `GET /diagnosis/{id}` — detail diagnosis
- [ ] `GET /knowledge` — list patterns knowledge base
- [ ] `GET /search?q=` — Atlas Full Text Search
- [ ] `POST /apply-index/{id}` — apply index (human-in-the-loop)
- [ ] `GET /metrics` — dashboard statistics
- [ ] Test semua endpoint via Swagger UI (`/docs`)

### ⬜ Hari 19–20 — Frontend: Dashboard + Diagnosis Page (28–29 Mei)
- [ ] Setup Next.js + Tailwind + shadcn/ui
- [ ] Dashboard (`/`):
  - Metric cards: Queries Detected, Avg Improvement, Patterns Learned
  - Tabel slow queries dengan status badges
  - Real-time polling setiap 5 detik
- [ ] Diagnosis detail (`/diagnosis/[id]`):
  - Panel kiri: raw query info
  - Panel kanan: Gemini diagnosis
  - Index suggestion + tombol Copy/Apply
  - Similar Past Cases cards

### ⬜ Hari 21–22 — Frontend: Knowledge Base + Polish (30–31 Mei)
- [ ] Knowledge Base page (`/knowledge`):
  - Search bar (Atlas Full Text Search)
  - Grid kartu patterns
  - Sort by frequency
- [ ] Responsive design
- [ ] Loading states + error handling
- [ ] Polish UI untuk demo-ready

---

## Fase 4: Deploy + Submit (Hari 23–32 | 1–10 Juni)

### ⬜ Hari 23–24 — Deploy Backend ke Railway (1–2 Juni)
- [ ] Test Dockerfile locally
- [ ] Deploy ke Railway.app
- [ ] Set environment variables di Railway
- [ ] Test semua endpoint di production URL

### ⬜ Hari 25–26 — Deploy Frontend ke Vercel (3–4 Juni)
- [ ] Deploy Next.js ke Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` ke Railway URL
- [ ] Test full flow di production
- [ ] Pastikan hosted URL bisa diakses judges

### ⬜ Hari 27–28 — Google Cloud Agent Builder (5–6 Juni)
- [ ] Aktifkan kredit $100 dari Devpost (jika sudah tersedia)
- [ ] Setup Agent Builder di GCP
- [ ] Integrasikan dengan existing pipeline
- [ ] Test compliance hackathon requirement

### ⬜ Hari 29–30 — Video Demo (7–8 Juni)
- [ ] Tulis script video (3 menit, Bahasa Inggris)
- [ ] Record demo: show full agent pipeline working
- [ ] Edit video
- [ ] Upload ke YouTube/Vimeo (public/unlisted)

### ⬜ Hari 31–32 — Final Polish + Submit (9–10 Juni)
- [ ] Final testing semua fitur
- [ ] Update README dengan screenshots
- [ ] Pastikan repo public + MIT License visible
- [ ] Submit di rapid-agent.devpost.com:
  - GitHub repo URL
  - Hosted URL (Vercel frontend)
  - Video demo URL
  - Deskripsi project

---

## Quick Reference

### Tech Stack
| Layer | Teknologi |
|---|---|
| AI/LLM | Gemini 2.5 Flash (Google AI Studio) |
| Embedding | gemini-embedding-001 (3072 dim) |
| Database | MongoDB Atlas M0 (free) |
| Backend | Python + FastAPI |
| Frontend | Next.js + shadcn/ui + Tailwind |
| Host BE | Railway.app |
| Host FE | Vercel |

### Environment Variables (backend/.env)
```
GEMINI_API_KEY=xxx
MONGODB_URI=mongodb+srv://...
MONGODB_DB=querysense
```

### Commands
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Test Gemini
python ../scripts/test_gemini.py

# Seed demo data
python ../scripts/seed_demo_data.py

# Frontend
cd frontend
npm run dev
```

### Hackathon Rules Checklist
- [ ] Menggunakan Gemini (Google AI)
- [ ] Menggunakan MongoDB MCP server secara meaningful
- [ ] Menggunakan Google Cloud Agent Builder
- [ ] Tidak pakai AI selain Google (no OpenAI/Anthropic)
- [ ] Project baru (dibuat Mei–Juni 2026)
- [ ] Repo public di GitHub + MIT License
- [ ] Hosted URL bisa diakses
- [ ] Video demo 3 menit (Bahasa Inggris)
