import os
import json
from typing import Dict, Any, Optional

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "data", "_ignored", "user_memory.json")


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)


def read_memory() -> Dict[str, Any]:
    """Read lightweight enterprise memory. Returns a dict with safe keys.
    Keys used:
      - language_preference: str in {"fr","en","darija"}
      - role: str (e.g., "Front Office")
      - department: str
      - focus_area: str (e.g., "Idoom Fibre")
    """
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh) or {}
    except Exception:
        return {}


def write_memory(update: Dict[str, Any]) -> None:
    """Persist safe memory entries. Only whitelisted keys are stored."""
    allowed = {"language_preference", "role", "department", "focus_area"}
    safe_update = {k: v for k, v in update.items() if k in allowed and isinstance(v, str) and len(v) <= 100}
    if not safe_update:
        return
    _ensure_dir(MEMORY_PATH)
    current = read_memory()
    current.update(safe_update)
    try:
        with open(MEMORY_PATH, "w", encoding="utf-8") as fh:
            json.dump(current, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


def reset_memory() -> None:
    """Delete memory safely."""
    try:
        if os.path.exists(MEMORY_PATH):
            os.remove(MEMORY_PATH)
    except Exception:
        pass


def extract_memory_facts(user_text: str) -> Dict[str, Any]:
    """Deterministic, rule-based extraction of explicit preferences.
    Only stores when the user clearly states a stable preference.
    Examples captured:
      - language preference (english/français/darija)
      - role (Front Office)
      - department (Commercial, Technique)
      - focus_area (Idoom Fibre, ADSL, VDSL)
    """
    t = (user_text or "").strip().lower()
    updates: Dict[str, Any] = {}

    # Language preference (explicit)
    if "prefer" in t or "préfér" in t or "prefere" in t:
        if "english" in t or "anglais" in t:
            updates["language_preference"] = "en"
        elif "français" in t or "francais" in t:
            updates["language_preference"] = "fr"
        elif "darija" in t or "arab" in t:
            updates["language_preference"] = "darija"

    # Role (explicit)
    if "front office" in t:
        updates["role"] = "Front Office"

    # Department (explicit)
    for dept in ("commercial", "technique", "marketing"):
        if dept in t:
            updates["department"] = dept.capitalize()
            break

    # Focus area (explicit)
    for area in ("idoom fibre", "adsl", "vdsl", "services internet"):
        if area in t:
            updates["focus_area"] = area.title()
            break

    return updates
