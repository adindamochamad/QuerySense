"""
Store — Menyimpan hasil analisis ke MongoDB Atlas sebagai knowledge base.
Setiap kasus baru memperkaya knowledge base via embedding.
"""

import os
from datetime import datetime, timezone

import google.generativeai as genai
from db.atlas import ambil_database

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def simpan_pattern(data_query: dict, diagnosa: dict, rekomendasi: dict) -> str:
    """
    Simpan pattern baru ke collection 'patterns' dengan embedding.
    Return: ID document yang baru disimpan.
    """
    db = await ambil_database()

    # Buat teks deskripsi untuk embedding
    teks_query = (
        f"filter by {data_query['filter']} sort by {data_query['sort']} "
        f"on {data_query['collection']}"
    )

    # Generate embedding menggunakan Google AI
    vektor_embedding = await _buat_embedding(teks_query)

    dokumen_pattern = {
        "query_text": teks_query,
        "embedding": vektor_embedding,
        "root_cause": diagnosa.get("root_cause", ""),
        "index_suggestion": rekomendasi.get("index_fields", {}),
        "collection_name": data_query["collection"],
        "estimated_improvement": rekomendasi.get("estimated_improvement", ""),
        "actual_improvement_ms": None,
        "frequency": 1,
        "resolved_at": datetime.now(timezone.utc),
    }

    hasil = await db.patterns.insert_one(dokumen_pattern)
    return str(hasil.inserted_id)


async def _buat_embedding(teks: str) -> list:
    """Generate embedding vector menggunakan Google gemini-embedding-001 (3072 dimensi)."""
    hasil = genai.embed_content(
        model="models/gemini-embedding-001",
        content=teks,
    )
    return hasil["embedding"]
