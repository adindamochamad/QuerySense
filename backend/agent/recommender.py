"""
Recommender — Menghasilkan rekomendasi index berdasarkan hasil diagnosis Gemini.
Output berupa createIndex() command yang siap dipakai.
"""

import json


def buat_rekomendasi_index(hasil_diagnosa: dict) -> dict:
    """
    Buat rekomendasi index dari hasil diagnosis.
    Return: dict dengan collection, index fields, dan estimasi improvement.
    """
    saran_index = hasil_diagnosa.get("index_suggestion", {})
    estimasi = hasil_diagnosa.get("estimated_improvement", "unknown")

    # Generate createIndex command yang siap dipakai
    perintah_index = _buat_perintah_create_index(saran_index)

    return {
        "index_fields": saran_index,
        "estimated_improvement": estimasi,
        "create_index_command": perintah_index,
        "explanation": hasil_diagnosa.get("explanation", ""),
    }


def _buat_perintah_create_index(index_fields: dict) -> str:
    """Generate string createIndex() command untuk MongoDB shell."""
    if not index_fields:
        return "// Tidak ada rekomendasi index"

    fields_json = json.dumps(index_fields)
    return f"db.collection.createIndex({fields_json})"
