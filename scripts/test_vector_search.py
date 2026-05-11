"""
Test Vector Search — Hari 3: Setup dan test Atlas Vector Search.
Jalankan: python scripts/test_vector_search.py

Script ini melakukan 3 hal:
1. Membuat Vector Search index di collection 'patterns'
2. Test embedding generation dengan text-embedding-004
3. Test $vectorSearch aggregation pipeline
"""

import os
import sys
import asyncio
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

import google.generativeai as genai
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from db.atlas import ambil_database, tutup_koneksi

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

NAMA_INDEX = "vector_index"
JUMLAH_DIMENSI = 3072
NAMA_MODEL_EMBEDDING = "models/gemini-embedding-001"


def buat_vector_search_index():
    """
    Membuat Atlas Vector Search index di collection 'patterns'.
    Menggunakan pymongo synchronous karena create_search_index
    tidak tersedia di Motor async driver.
    """
    uri_mongo = os.getenv("MONGODB_URI")
    nama_db = os.getenv("MONGODB_DB", "querysense")

    klien = MongoClient(uri_mongo)
    koleksi = klien[nama_db]["patterns"]

    # Cek apakah index sudah ada — hapus jika dimensi tidak sesuai
    daftar_index = list(koleksi.list_search_indexes())
    for idx in daftar_index:
        if idx.get("name") == NAMA_INDEX:
            definisi = idx.get("latestDefinition", {})
            fields = definisi.get("fields", [])
            dimensi_lama = None
            for f in fields:
                if f.get("path") == "embedding":
                    dimensi_lama = f.get("numDimensions")
            if dimensi_lama == JUMLAH_DIMENSI:
                print(f"ℹ️  Vector Search index '{NAMA_INDEX}' sudah ada ({JUMLAH_DIMENSI} dim), skip.")
                klien.close()
                return True
            else:
                print(f"⚠️  Index lama ditemukan ({dimensi_lama} dim), menghapus untuk buat ulang...")
                koleksi.drop_search_index(NAMA_INDEX)
                import time as _time
                _time.sleep(3)

    # Definisi vector search index
    model_index = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": JUMLAH_DIMENSI,
                    "similarity": "cosine",
                }
            ]
        },
        name=NAMA_INDEX,
        type="vectorSearch",
    )

    print(f"🔧 Membuat Vector Search index '{NAMA_INDEX}'...")
    print(f"   - Field: embedding")
    print(f"   - Dimensi: {JUMLAH_DIMENSI}")
    print(f"   - Similarity: cosine")

    try:
        hasil = koleksi.create_search_index(model=model_index)
        print(f"✅ Index berhasil dibuat: {hasil}")
        print("⏳ Index sedang di-build oleh Atlas (biasanya 1-2 menit)...")
    except Exception as e:
        pesan_error = str(e)
        if "already exists" in pesan_error.lower() or "duplicate" in pesan_error.lower():
            print(f"ℹ️  Index sudah ada: {pesan_error}")
        else:
            print(f"❌ Gagal membuat index: {e}")
            klien.close()
            return False

    klien.close()
    return True


def test_embedding():
    """Test embedding generation menggunakan gemini-embedding-001."""
    print(f"\n📐 Testing embedding generation ({NAMA_MODEL_EMBEDDING})...")

    contoh_teks = [
        "filter by status pending sort by created_at on orders",
        "filter by email sort by none on users",
        "filter by category electronics price lt 500 sort by rating on products",
    ]

    for teks in contoh_teks:
        hasil = genai.embed_content(
            model=NAMA_MODEL_EMBEDDING,
            content=teks,
        )
        vektor = hasil["embedding"]
        panjang_vektor = len(vektor)

        status = "✅" if panjang_vektor == JUMLAH_DIMENSI else "❌"
        print(f"   {status} \"{teks[:50]}...\"")
        print(f"      → {panjang_vektor} dimensi | sample: [{vektor[0]:.6f}, {vektor[1]:.6f}, ..., {vektor[-1]:.6f}]")

        if panjang_vektor != JUMLAH_DIMENSI:
            print(f"      ⚠️  PERINGATAN: Ekspektasi {JUMLAH_DIMENSI} dimensi, dapat {panjang_vektor}")
            return False

    print(f"✅ Semua embedding berhasil ({JUMLAH_DIMENSI} dimensi)")
    return True


async def sisipkan_contoh_patterns():
    """Sisipkan beberapa pattern dengan embedding ke collection patterns untuk testing."""
    db = await ambil_database()

    # Hapus patterns lama yang mungkin punya embedding dimensi berbeda
    jumlah_existing = await db.patterns.count_documents({})
    if jumlah_existing > 0:
        print(f"\n🗑️  Membersihkan {jumlah_existing} pattern lama (mungkin dimensi berbeda)...")
        await db.patterns.delete_many({})
    print("   Menyisipkan 3 contoh pattern baru dengan embedding yang benar...")

    contoh_patterns = [
        {
            "query_text": "filter by status pending sort by created_at on orders",
            "root_cause": "Missing compound index on {status, created_at}",
            "index_suggestion": {"status": 1, "created_at": -1},
            "collection_name": "orders",
            "estimated_improvement": "85%",
            "frequency": 5,
        },
        {
            "query_text": "filter by email sort by none on users",
            "root_cause": "Missing unique index on email field",
            "index_suggestion": {"email": 1},
            "collection_name": "users",
            "estimated_improvement": "95%",
            "frequency": 3,
        },
        {
            "query_text": "filter by category and price sort by rating on products",
            "root_cause": "Missing compound index on {category, price, rating}",
            "index_suggestion": {"category": 1, "price": 1, "rating": -1},
            "collection_name": "products",
            "estimated_improvement": "78%",
            "frequency": 2,
        },
    ]

    id_tersimpan = []
    for pola in contoh_patterns:
        # Buat embedding untuk setiap pattern
        hasil_embed = genai.embed_content(
            model=NAMA_MODEL_EMBEDDING,
            content=pola["query_text"],
        )
        pola["embedding"] = hasil_embed["embedding"]

        hasil_insert = await db.patterns.insert_one(pola)
        id_tersimpan.append(hasil_insert.inserted_id)
        print(f"   📝 Tersimpan: {pola['query_text'][:50]}...")

    print(f"✅ {len(id_tersimpan)} pattern dengan embedding berhasil disimpan")
    return id_tersimpan


async def test_vector_search():
    """Test $vectorSearch aggregation pipeline."""
    db = await ambil_database()

    # Buat embedding untuk query pencarian
    teks_pencarian = "filter by status sort by created_at on orders"
    print(f"\n🔍 Mencari kasus serupa untuk: \"{teks_pencarian}\"")

    hasil_embed = genai.embed_content(
        model=NAMA_MODEL_EMBEDDING,
        content=teks_pencarian,
    )
    vektor_pencarian = hasil_embed["embedding"]

    pipeline = [
        {
            "$vectorSearch": {
                "index": NAMA_INDEX,
                "path": "embedding",
                "queryVector": vektor_pencarian,
                "numCandidates": 30,
                "limit": 3,
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
        hasil_pencarian = await cursor.to_list(length=3)

        if not hasil_pencarian:
            print("⚠️  Tidak ada hasil. Index mungkin masih di-build oleh Atlas.")
            print("   Tunggu 1-2 menit lalu jalankan script ini lagi.")
            return False

        print(f"✅ Ditemukan {len(hasil_pencarian)} kasus serupa:\n")
        for i, kasus in enumerate(hasil_pencarian, 1):
            print(f"   #{i} (score: {kasus.get('score', 0):.4f})")
            print(f"      Query: {kasus.get('query_text', '-')}")
            print(f"      Root Cause: {kasus.get('root_cause', '-')}")
            print(f"      Index: {json.dumps(kasus.get('index_suggestion', {}))}")
            print(f"      Improvement: {kasus.get('estimated_improvement', '-')}")
            print()

        return True

    except Exception as e:
        pesan_error = str(e)
        if "index not found" in pesan_error.lower() or "not ready" in pesan_error.lower():
            print(f"⏳ Index belum siap: {pesan_error}")
            print("   Atlas masih membangun index. Tunggu 1-2 menit lalu coba lagi.")
        else:
            print(f"❌ Error saat $vectorSearch: {e}")
        return False


async def main():
    print("=" * 60)
    print("  QuerySense — Hari 3: Setup Atlas Vector Search")
    print("=" * 60)

    # Langkah 1: Buat Vector Search index
    print("\n📌 LANGKAH 1: Membuat Vector Search Index")
    print("-" * 50)
    sukses_index = buat_vector_search_index()
    if not sukses_index:
        print("❌ Gagal membuat index. Hentikan proses.")
        sys.exit(1)

    # Langkah 2: Test embedding
    print("\n📌 LANGKAH 2: Test Embedding (text-embedding-004)")
    print("-" * 50)
    sukses_embedding = test_embedding()
    if not sukses_embedding:
        print("❌ Embedding test gagal. Hentikan proses.")
        sys.exit(1)

    # Langkah 3: Sisipkan contoh patterns
    print("\n📌 LANGKAH 3: Sisipkan Contoh Patterns dengan Embedding")
    print("-" * 50)
    try:
        await sisipkan_contoh_patterns()
    except Exception as e:
        print(f"❌ Gagal menyisipkan patterns: {e}")
        sys.exit(1)

    # Langkah 4: Test $vectorSearch
    print("\n📌 LANGKAH 4: Test $vectorSearch Aggregation Pipeline")
    print("-" * 50)

    # Beri jeda sedikit agar Atlas punya waktu index data baru
    print("⏳ Menunggu 5 detik agar index meng-update data baru...")
    await asyncio.sleep(5)

    sukses_pencarian = await test_vector_search()

    # Ringkasan akhir
    print("\n" + "=" * 60)
    print("  RINGKASAN HARI 3")
    print("=" * 60)
    print(f"  ✅ Vector Search Index  : {'Berhasil' if sukses_index else 'Gagal'}")
    print(f"  ✅ Embedding Test       : {'Berhasil' if sukses_embedding else 'Gagal'}")
    print(f"  {'✅' if sukses_pencarian else '⏳'} $vectorSearch Test    : {'Berhasil' if sukses_pencarian else 'Menunggu index siap'}")

    if not sukses_pencarian:
        print("\n💡 Jika $vectorSearch belum berhasil:")
        print("   Index Atlas membutuhkan 1-2 menit untuk build.")
        print("   Jalankan ulang script ini setelah menunggu sebentar.")

    print()
    await tutup_koneksi()


if __name__ == "__main__":
    asyncio.run(main())
