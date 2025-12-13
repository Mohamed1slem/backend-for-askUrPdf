from typing import List, Dict, Any, Tuple
import os


def _doc_id_from_chunk(chunk: Dict[str, Any]) -> str:
    """Return canonical document id (basename of original source)."""
    src = chunk.get("original_source") or chunk.get("source") or ""
    return os.path.basename(src)


def _merge_metadata(md_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge metadata by choosing the first non-empty value per key."""
    out: Dict[str, Any] = {}
    keys = {k for md in md_list for k in (md or {}).keys()}

    for k in keys:
        for md in md_list:
            v = (md or {}).get(k)
            if isinstance(v, str):
                v = v.strip()
            if v:
                out[k] = v
                break
        if k not in out:
            out[k] = ""

    return out


def build_document_graph(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a deterministic, métier-aware document graph.

    Rules:
    - Only link Convention ↔ Offres / Offres en arabe
    - Never link Convention ↔ Convention or Offre ↔ Offre
    - Exclude Guide NGBSS and Dépot Vente
    - partner must match (case-insensitive)
    - if both have offer_type, it must also match
    - cap links per Convention to MAX_LINKS_PER_CONVENTION
    """
    # Group chunks by document id
    doc_chunks: Dict[str, List[Dict[str, Any]]] = {}
    for ch in chunks:
        did = _doc_id_from_chunk(ch)
        if not did:
            continue
        doc_chunks.setdefault(did, []).append(ch)

    # Build document-level metadata
    documents: Dict[str, Dict[str, Any]] = {}
    for did, group in doc_chunks.items():
        md_list = [c.get("metadata", {}) for c in group]
        merged = _merge_metadata(md_list)
        merged["document_id"] = did
        documents[did] = merged

    def norm(s: Any) -> str:
        return (s or "").strip().lower()

    conventions: List[str] = []
    offers: List[str] = []

    for did, md in documents.items():
        cat = norm(md.get("category"))
        if cat == "convention":
            conventions.append(did)
        elif cat in ("offres", "offres en arabe"):
            offers.append(did)

    conventions.sort()
    offers.sort()

    MAX_LINKS_PER_CONVENTION = 5
    links: List[Dict[str, Any]] = []

    for c_id in conventions:
        md_c = documents[c_id]
        partner_c = norm(md_c.get("partner"))
        offer_c = norm(md_c.get("offer_type"))

        if not partner_c:
            continue

        candidates: List[str] = []

        for o_id in offers:
            md_o = documents[o_id]
            partner_o = norm(md_o.get("partner"))
            offer_o = norm(md_o.get("offer_type"))

            if partner_o != partner_c:
                continue
            if offer_c and offer_o and offer_c != offer_o:
                continue

            candidates.append(o_id)

        # deterministic order
        candidates.sort()

        for o_id in candidates[:MAX_LINKS_PER_CONVENTION]:
            links.append({
                "source": c_id,
                "target": o_id,
                "relation": "offer_convention_link"
            })

    return {
        "documents": documents,
        "links": links
    }


def integrate_graph_into_chunks(
    chunks: List[Dict[str, Any]],
    graph: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Attach related document ids to each chunk."""
    adj: Dict[str, set] = {}

    for link in graph.get("links", []):
        s = link.get("source")
        t = link.get("target")
        if not s or not t:
            continue
        adj.setdefault(s, set()).add(t)
        adj.setdefault(t, set()).add(s)

    out: List[Dict[str, Any]] = []
    for ch in chunks:
        did = _doc_id_from_chunk(ch)
        new_ch = dict(ch)
        new_ch["links"] = sorted(adj.get(did, set()))
        out.append(new_ch)

    return out
