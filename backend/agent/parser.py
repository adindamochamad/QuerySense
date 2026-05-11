"""
Parser — Mengekstrak informasi penting dari raw profiler log
menjadi format yang siap diproses oleh Gemini.
"""


def parse_query_log(raw_log: dict) -> dict:
    """
    Parse raw profiler document menjadi struktur yang bersih.
    """
    namespace = raw_log.get("ns", "")
    bagian_ns = namespace.split(".")
    nama_collection = bagian_ns[-1] if len(bagian_ns) > 1 else namespace

    command = raw_log.get("command", {})
    filter_query = command.get("filter", {})
    sort_query = command.get("sort", {})

    return {
        "namespace": namespace,
        "collection": nama_collection,
        "filter": filter_query,
        "sort": sort_query,
        "millis": raw_log.get("millis", 0),
        "plan_summary": raw_log.get("planSummary", "UNKNOWN"),
        "raw": raw_log,
    }
