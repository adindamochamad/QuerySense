"""
Interceptor — Poll MongoDB system.profile untuk mendeteksi slow queries.
Filter query dengan execution time > threshold (default: 100ms).
"""

from db.atlas import ambil_database

BATAS_WAKTU_MS = 100


async def ambil_slow_queries(batas_ms: int = BATAS_WAKTU_MS) -> list:
    """
    Ambil slow queries dari db.system.profile yang melebihi batas waktu.
    """
    db = await ambil_database()

    filter_query = {"millis": {"$gt": batas_ms}}
    projection = {
        "ns": 1,
        "command": 1,
        "millis": 1,
        "planSummary": 1,
        "ts": 1,
    }

    cursor = db.system.profile.find(filter_query, projection).sort("ts", -1).limit(50)
    hasil = await cursor.to_list(length=50)

    return hasil
