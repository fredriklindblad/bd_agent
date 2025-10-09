# =========================
# analyze_agent/utils.py
# Utils
# =========================

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def _load_yaml_params(path: str = "config/params.yaml") -> Dict[str, Any]:
    full = path if os.path.isabs(path) else os.path.join(PROJECT_ROOT, path)
    with open(full, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def clean_query(user_prompt: str) -> str:
    q = user_prompt.strip()
    q = re.sub(
        r"^\s*(analy[sz]e|analysera|analys)\b", "", q, flags=re.IGNORECASE
    ).strip()
    return q or user_prompt.strip()


def _clean_name(n: str) -> str:
    u = n.upper()
    u = re.sub(r"\bAB\s*\(PUBL\)\b", "", u)
    u = re.sub(r"\b\(PUBL\)\b", "", u)
    u = re.sub(r"\bAB\b", "", u)
    u = re.sub(r"\bSER\.?\s*[A-Z]\b", "", u)
    u = re.sub(r"\s+", " ", u)
    return u.strip()


def to_float(x: Any) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None


def fmt_rule(op: str, limit: Optional[float]) -> Optional[str]:
    return f"{op} {limit}" if limit is not None else None


def ratio_pass(
    value: Optional[float], op: str, limit: Optional[float]
) -> Optional[bool]:
    if value is None or limit is None:
        return None
    if op == "<=":
        return value <= limit
    if op == ">=":
        return value >= limit
    return None


def _extract_year(as_of: Optional[str]) -> Optional[int]:
    if not as_of:
        return None
    m = re.search(r"(\d{4})", as_of)
    return int(m.group(1)) if m else None
