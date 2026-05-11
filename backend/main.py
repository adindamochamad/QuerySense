"""
QuerySense Backend — FastAPI Entry Point
Slow Query Detective Agent untuk MongoDB
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="QuerySense API",
    description="Slow Query Detective Agent — AI-powered MongoDB query optimizer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "nama_aplikasi": "QuerySense",
        "versi": "0.1.0",
        "deskripsi": "Slow Query Detective Agent",
        "status": "aktif",
    }


@app.get("/metrics")
async def ambil_metrik():
    """Statistik: total terdeteksi, rata-rata improvement, patterns learned"""
    return {
        "total_terdeteksi": 0,
        "rata_rata_improvement_persen": 0,
        "total_patterns": 0,
    }
