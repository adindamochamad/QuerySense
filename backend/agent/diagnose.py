"""
Diagnose — Menggunakan Gemini untuk menganalisis root cause slow query.
Mencari similar past cases via Vector Search sebelum mengirim ke Gemini.
"""

import json
import os
import google.generativeai as genai
from db.vector_search import cari_kasus_serupa

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_DIAGNOSA = """
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


async def diagnosa_dengan_gemini(data_query: dict) -> dict:
    """
    Kirim slow query ke Gemini untuk diagnosis.
    Sertakan similar past cases dari Vector Search sebagai konteks.
    """

    # Cari kasus serupa dari knowledge base
    kasus_serupa = await cari_kasus_serupa(data_query)
    teks_kasus_serupa = _format_kasus_serupa(kasus_serupa)

    # Buat prompt untuk Gemini
    prompt = PROMPT_DIAGNOSA.format(
        collection=data_query["collection"],
        query_filter=json.dumps(data_query["filter"]),
        sort=json.dumps(data_query["sort"]),
        millis=data_query["millis"],
        plan_summary=data_query["plan_summary"],
        similar_cases=teks_kasus_serupa,
    )

    # Panggil Gemini
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    # Parse response JSON
    try:
        teks_hasil = response.text.strip()
        if teks_hasil.startswith("```"):
            teks_hasil = teks_hasil.split("\n", 1)[1].rsplit("```", 1)[0]
        hasil = json.loads(teks_hasil)
    except (json.JSONDecodeError, IndexError):
        hasil = {
            "root_cause": response.text,
            "index_suggestion": {},
            "estimated_improvement": "unknown",
            "explanation": response.text,
            "confidence": 0.5,
        }

    return hasil


def _format_kasus_serupa(kasus_list: list) -> str:
    """Format list kasus serupa menjadi teks untuk prompt."""
    if not kasus_list:
        return "No similar past cases found."

    bagian_teks = []
    for i, kasus in enumerate(kasus_list, 1):
        bagian_teks.append(
            f"{i}. Collection: {kasus.get('collection_name', 'unknown')}\n"
            f"   Root cause: {kasus.get('root_cause', 'unknown')}\n"
            f"   Index: {kasus.get('index_suggestion', {})}\n"
            f"   Improvement: {kasus.get('estimated_improvement', 'unknown')}"
        )

    return "\n".join(bagian_teks)
