#!/usr/bin/env python3
import argparse
import json
import time
import csv
import hashlib
from typing import List, Dict, Any

import requests


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", errors="ignore")).hexdigest()


def load_queries(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Test queries file must be a JSON array of objects")
    return data


def call_search(api_base: str, query: str, filters: List[str], top_k: int) -> Dict[str, Any]:
    url = api_base.rstrip("/") + "/search"
    body = {"query": query, "filters": filters or []}
    # Measure latency
    t0 = time.time()
    resp = requests.post(url, json=body, timeout=60)
    t1 = time.time()
    latency_ms = (t1 - t0) * 1000.0
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    if isinstance(results, list) and top_k:
        results = results[:top_k]
    return {"results": results, "latency_ms": latency_ms}


def metadata_complete(meta: Dict[str, Any]) -> bool:
    required = ["category", "partner", "offer_type", "sector"]
    for k in required:
        v = (meta or {}).get(k, "")
        if not isinstance(v, str) or not v.strip():
            return False
    return True


def evaluate_query(api_base: str, q: Dict[str, Any], top_k: int) -> Dict[str, Any]:
    query_text = q.get("query") or q.get("question") or ""
    filters = q.get("filters", [])
    res = call_search(api_base, query_text, filters, top_k)
    results = res["results"]
    latency_ms = res["latency_ms"]

    total = len(results)
    hashes = []
    dup_count = 0
    complete_meta_count = 0

    seen = set()
    for r in results:
        chunk_text = r.get("chunk", "")
        h = sha256_text(chunk_text)
        hashes.append(h)
        if h in seen:
            dup_count += 1
        else:
            seen.add(h)

        if metadata_complete(r.get("metadata", {})):
            complete_meta_count += 1

    dedup_rate = (dup_count / total * 100.0) if total > 0 else 0.0
    meta_rate = (complete_meta_count / total * 100.0) if total > 0 else 0.0

    return {
        "query": query_text,
        "filters": ",".join(filters) if isinstance(filters, list) else str(filters),
        "num_results": total,
        "dup_chunks": dup_count,
        "dedup_rate_pct": round(dedup_rate, 2),
        "metadata_complete_pct": round(meta_rate, 2),
        "latency_ms": round(latency_ms, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate document search pipeline")
    parser.add_argument("queries", help="Path to JSON file with test queries (array of objects)")
    parser.add_argument("--api-base", default="http://localhost:8000", help="Base URL for the API")
    parser.add_argument("--top-k", type=int, default=10, help="Number of top results to consider per query")
    parser.add_argument("--out", default="search_eval.csv", help="CSV output file for per-query stats")
    args = parser.parse_args()

    queries = load_queries(args.queries)
    rows = []
    latencies = []

    for q in queries:
        stats = evaluate_query(args.api_base, q, args.top_k)
        rows.append(stats)
        latencies.append(stats["latency_ms"])

        # Print report for each query
        print("-" * 60)
        print(f"Query: {stats['query']}")
        print(f"Filters: {stats['filters']}")
        print(f"Results: {stats['num_results']}")
        print(f"Duplicate chunks: {stats['dup_chunks']}")
        print(f"Deduplication rate: {stats['dedup_rate_pct']}%")
        print(f"Metadata completeness: {stats['metadata_complete_pct']}%")
        print(f"Latency: {stats['latency_ms']} ms")

    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    print("=" * 60)
    print(f"Average search latency: {avg_latency} ms over {len(latencies)} queries")

    # Write CSV
    fieldnames = [
        "query", "filters", "num_results", "dup_chunks",
        "dedup_rate_pct", "metadata_complete_pct", "latency_ms"
    ]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Saved per-query stats to {args.out}")


if __name__ == "__main__":
    main()
