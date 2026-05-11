"""
Vector Search — Mencari kasus serupa menggunakan MongoDB Atlas $vectorSearch.
"""

import json
import os

import google.generativeai as genai
from db.atlas import ambil_database

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

NAMA_INDEX_VECTOR = "vector_index"
JUMLAH_HASIL_PENCARIAN = 3


async def cari_kasus_serupa(data_query: dict, limit: int = JUMLAH_HASIL_PENCARIAN) -> list:
    """
    Cari 3 kasus paling mirip dari collection 'patterns'
    menggunakan Atlas $vectorSearch berdasarkan embedding query.
    """
    db = await ambil_database()

    # Buat embedding dari query yang sedang dianalisis
    teks_query = (
        f"filter by {json.dumps(data_query['filter'])} "
        f"sort by {json.dumps(data_query['sort'])} "
        f"on {data_query['collection']}"
    )

    vektor_query = await _buat_embedding(teks_query)

    # Jalankan $vectorSearch aggregation
    pipeline = [
        {
            "$vectorSearch": {
                "index": NAMA_INDEX_VECTOR,
                "path": "embedding",
                "queryVector": vektor_query,
                "numCandidates": limit * 10,
                "limit": limit,
            }
        },
        {
            "$project": {
                "query_text": 1,
                "root_cause": 1,
                "index_suggestion": 1,
                "collection_name": 1,
                "estimated_improvement": 1,
                "frequency": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    try:
        cursor = db.patterns.aggregate(pipeline)
        hasil = await cursor.to_list(length=limit)
    except Exception:
        hasil = []

    return hasil


async def _buat_embedding(teks: str) -> list:
    """Generate embedding vector menggunakan Google gemini-embedding-001 (3072 dimensi)."""
    hasil = genai.embed_content(
        model="models/gemini-embedding-001",
        content=teks,
    )
    return hasil["embedding"]
