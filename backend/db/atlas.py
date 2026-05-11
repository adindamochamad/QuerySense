"""
Atlas — Koneksi ke MongoDB Atlas menggunakan Motor (async driver).
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient

_client = None
_database = None


async def ambil_database():
    """
    Ambil instance database MongoDB. Menggunakan singleton pattern
    agar koneksi tidak dibuat berulang kali.
    """
    global _client, _database

    if _database is None:
        uri_mongo = os.getenv("MONGODB_URI")
        nama_db = os.getenv("MONGODB_DB", "querysense")

        if not uri_mongo:
            raise ValueError("MONGODB_URI belum di-set di environment variables")

        _client = AsyncIOMotorClient(uri_mongo)
        _database = _client[nama_db]

    return _database


async def tutup_koneksi():
    """Tutup koneksi MongoDB saat aplikasi shutdown."""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
