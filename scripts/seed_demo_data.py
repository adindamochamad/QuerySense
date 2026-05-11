"""
Seed Demo Data — Generate 20+ dummy slow query patterns untuk demo.
Jalankan: python scripts/seed_demo_data.py
"""

import os
import sys
import asyncio
from datetime import datetime, timezone, timedelta
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from db.atlas import ambil_database

# Data dummy untuk simulasi slow queries
CONTOH_QUERY_LOGS = [
    {
        "ns": "querysense.orders",
        "command": {"filter": {"status": "pending"}, "sort": {"created_at": -1}},
        "millis": 2340,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.orders",
        "command": {"filter": {"user_id": 123, "status": "shipped"}, "sort": {"updated_at": -1}},
        "millis": 1890,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.products",
        "command": {"filter": {"category": "electronics", "price": {"$lt": 500}}, "sort": {"rating": -1}},
        "millis": 3100,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.users",
        "command": {"filter": {"email": "user@example.com"}, "sort": {}},
        "millis": 890,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.orders",
        "command": {"filter": {"created_at": {"$gte": "2024-01-01"}}, "sort": {"total": -1}},
        "millis": 4500,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.reviews",
        "command": {"filter": {"product_id": 456, "rating": {"$gte": 4}}, "sort": {"created_at": -1}},
        "millis": 1200,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.sessions",
        "command": {"filter": {"user_id": 789, "active": True}, "sort": {"last_activity": -1}},
        "millis": 670,
        "planSummary": "IXSCAN",
    },
    {
        "ns": "querysense.logs",
        "command": {"filter": {"level": "error", "service": "payment"}, "sort": {"timestamp": -1}},
        "millis": 5600,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.inventory",
        "command": {"filter": {"warehouse_id": 3, "quantity": {"$lt": 10}}, "sort": {"product_name": 1}},
        "millis": 980,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.transactions",
        "command": {"filter": {"type": "refund", "amount": {"$gt": 100}}, "sort": {"processed_at": -1}},
        "millis": 2100,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.notifications",
        "command": {"filter": {"user_id": 101, "read": False}, "sort": {"created_at": -1}},
        "millis": 1450,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.products",
        "command": {"filter": {"tags": {"$in": ["sale", "featured"]}}, "sort": {"views": -1}},
        "millis": 3800,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.orders",
        "command": {"filter": {"payment_status": "failed"}, "sort": {"retry_count": -1}},
        "millis": 1670,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.users",
        "command": {"filter": {"role": "admin", "active": True}, "sort": {"last_login": -1}},
        "millis": 430,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.analytics",
        "command": {"filter": {"event": "page_view", "page": "/checkout"}, "sort": {"timestamp": -1}},
        "millis": 7200,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.shipments",
        "command": {"filter": {"carrier": "fedex", "status": "in_transit"}, "sort": {"estimated_delivery": 1}},
        "millis": 1890,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.coupons",
        "command": {"filter": {"valid_until": {"$gte": "2026-05-01"}, "used": False}, "sort": {"discount": -1}},
        "millis": 560,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.messages",
        "command": {"filter": {"conversation_id": "abc123", "deleted": False}, "sort": {"sent_at": 1}},
        "millis": 2900,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.payments",
        "command": {"filter": {"method": "credit_card", "currency": "USD"}, "sort": {"amount": -1}},
        "millis": 1340,
        "planSummary": "COLLSCAN",
    },
    {
        "ns": "querysense.audit_logs",
        "command": {"filter": {"action": "delete", "resource": "user"}, "sort": {"performed_at": -1}},
        "millis": 4100,
        "planSummary": "COLLSCAN",
    },
]


async def seed_query_logs():
    """Masukkan dummy slow query logs ke collection query_logs."""
    db = await ambil_database()

    daftar_dokumen = []
    for i, log in enumerate(CONTOH_QUERY_LOGS):
        waktu_acak = datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
        status_list = ["detected", "analyzing", "resolved"]
        bobot_status = [0.4, 0.3, 0.3]

        daftar_dokumen.append({
            "ns": log["ns"],
            "query": log["command"].get("filter", {}),
            "sort": log["command"].get("sort", {}),
            "millis": log["millis"],
            "plan_summary": log["planSummary"],
            "status": random.choices(status_list, weights=bobot_status, k=1)[0],
            "created_at": waktu_acak,
        })

    hasil = await db.query_logs.insert_many(daftar_dokumen)
    print(f"✅ Berhasil insert {len(hasil.inserted_ids)} query logs")


async def main():
    print("🌱 Seeding demo data ke MongoDB Atlas...")
    print("-" * 50)

    await seed_query_logs()

    print("-" * 50)
    print("🎉 Seeding selesai!")


if __name__ == "__main__":
    asyncio.run(main())
