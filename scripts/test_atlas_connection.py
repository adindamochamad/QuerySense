"""
Test Atlas Connection — Verifikasi koneksi ke MongoDB Atlas.
Jalankan: python scripts/test_atlas_connection.py
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from db.atlas import ambil_database, tutup_koneksi


async def main():
    uri_mongo = os.getenv("MONGODB_URI")
    nama_db = os.getenv("MONGODB_DB", "querysense")

    if not uri_mongo or "user:password" in uri_mongo:
        print("❌ ERROR: MONGODB_URI belum diupdate di backend/.env!")
        print("   Ganti placeholder dengan connection string dari Atlas.")
        sys.exit(1)

    print(f"🔗 Menghubungkan ke MongoDB Atlas...")
    print(f"   Database: {nama_db}")
    print("-" * 50)

    try:
        db = await ambil_database()

        # Tes ping ke server
        hasil_ping = await db.command("ping")
        print(f"✅ Ping berhasil: {hasil_ping}")

        # Tampilkan daftar collection yang ada
        daftar_collection = await db.list_collection_names()
        print(f"\n📦 Collections di database '{nama_db}':")
        if daftar_collection:
            for nama in sorted(daftar_collection):
                jumlah_doc = await db[nama].count_documents({})
                print(f"   - {nama} ({jumlah_doc} dokumen)")
        else:
            print("   (belum ada collection)")

        # Tes insert + delete untuk pastikan write access
        koleksi_tes = db["_test_koneksi"]
        hasil_insert = await koleksi_tes.insert_one({"tes": True})
        await koleksi_tes.delete_one({"_id": hasil_insert.inserted_id})
        print(f"\n✅ Write access berhasil (insert + delete test)")

        print("-" * 50)
        print("🎉 Koneksi MongoDB Atlas berfungsi sempurna!")

    except Exception as e:
        print(f"❌ ERROR: Gagal terhubung ke MongoDB Atlas")
        print(f"   Detail: {e}")
        print("\n💡 Tips:")
        print("   1. Pastikan connection string benar di backend/.env")
        print("   2. Pastikan IP kamu sudah di-whitelist di Atlas")
        print("   3. Pastikan username/password benar")
        sys.exit(1)
    finally:
        await tutup_koneksi()


if __name__ == "__main__":
    asyncio.run(main())
