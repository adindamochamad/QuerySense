"""
Orchestrator — Mengatur 4-step pipeline agent:
1. Intercept → 2. Diagnose → 3. Recommend → 4. Store & Learn
"""

from agent.interceptor import ambil_slow_queries
from agent.parser import parse_query_log
from agent.diagnose import diagnosa_dengan_gemini
from agent.recommender import buat_rekomendasi_index
from agent.store import simpan_pattern


async def jalankan_pipeline(query_log: dict) -> dict:
    """
    Menjalankan full pipeline analisis untuk satu slow query.
    Return: hasil diagnosis lengkap dengan rekomendasi index.
    """

    # Step 1: Parse query log dari profiler
    data_query = parse_query_log(query_log)

    # Step 2: Diagnosa root cause menggunakan Gemini
    hasil_diagnosa = await diagnosa_dengan_gemini(data_query)

    # Step 3: Generate rekomendasi index
    rekomendasi = buat_rekomendasi_index(hasil_diagnosa)

    # Step 4: Simpan ke knowledge base
    await simpan_pattern(data_query, hasil_diagnosa, rekomendasi)

    return {
        "query": data_query,
        "diagnosa": hasil_diagnosa,
        "rekomendasi": rekomendasi,
        "status": "resolved",
    }
