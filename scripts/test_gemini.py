"""
Test Gemini API — Verifikasi bahwa API key berfungsi dengan benar.
Jalankan: python scripts/test_gemini.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY belum di-set!")
    print("   Buat file backend/.env dengan isi:")
    print("   GEMINI_API_KEY=your_api_key_here")
    sys.exit(1)

genai.configure(api_key=api_key)

print("🔑 API Key ditemukan, menguji koneksi ke Gemini...")
print("-" * 50)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(
        "Analyze this MongoDB slow query: "
        "db.orders.find({status: 'pending'}).sort({created_at: -1}) "
        "took 2340ms. Why is it slow? Answer in 3 sentences."
    )
    print("✅ Gemini berhasil merespons!\n")
    print("Response:")
    print(response.text)
    print("-" * 50)
    print("\n🎉 Setup Hari 1 selesai! API key valid dan Gemini berfungsi.")
except Exception as e:
    print(f"❌ ERROR: Gagal menghubungi Gemini API")
    print(f"   Detail: {e}")
    sys.exit(1)
