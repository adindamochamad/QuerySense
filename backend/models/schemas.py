"""
Schemas — Pydantic models untuk validasi data request/response API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QueryLogInput(BaseModel):
    """Schema untuk input manual analysis."""
    ns: str = Field(..., description="Namespace (database.collection)")
    query: dict = Field(default_factory=dict, description="Filter query")
    sort: dict = Field(default_factory=dict, description="Sort specification")
    millis: int = Field(..., description="Waktu eksekusi dalam milliseconds")
    plan_summary: str = Field(default="COLLSCAN", description="Execution plan summary")


class QueryLogResponse(BaseModel):
    """Schema untuk response query log."""
    id: str
    ns: str
    query: dict
    sort: dict
    millis: int
    plan_summary: str
    status: str = "detected"
    created_at: datetime


class DiagnosisResponse(BaseModel):
    """Schema untuk response diagnosis lengkap."""
    id: str
    query: dict
    diagnosa: dict
    rekomendasi: dict
    kasus_serupa: list = []
    status: str


class PatternResponse(BaseModel):
    """Schema untuk response knowledge base pattern."""
    id: str
    query_text: str
    root_cause: str
    index_suggestion: dict
    collection_name: str
    estimated_improvement: str
    frequency: int = 1
    resolved_at: Optional[datetime] = None


class MetricsResponse(BaseModel):
    """Schema untuk response metrics dashboard."""
    total_terdeteksi: int = 0
    rata_rata_improvement_persen: float = 0.0
    total_patterns: int = 0
