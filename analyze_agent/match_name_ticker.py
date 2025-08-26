# =========================
# Matchning: Instrument[name] -> Instrument[ticker]
# =========================

import re
from typing import List, Tuple
from bd.bd_client import BorsdataClient
from bd.bd_models import Instrument
from analyze_agent.utils import (clean_query, _clean_name)

def _iter_instruments(bd: BorsdataClient) -> List[Instrument]:
    """Returnerar en lista av bd_models.Instrument (coercar om klienten levererar dicts)."""
    raw = getattr(bd, "instruments", [])
    out: List[Instrument] = []
    for it in raw:
        if isinstance(it, Instrument):
            out.append(it)
        elif isinstance(it, dict):
            # försök mappa dict -> Instrument
            try:
                out.append(Instrument(**{
                    "id": it.get("id") or it.get("ins_id") or it.get("InsId") or it.get("insId"),
                    "name": it.get("name") or it.get("Name"),
                    "ticker": it.get("ticker") or it.get("Ticker"),
                    "instrument_type": it.get("instrument_type"),
                    "isin": it.get("isin"),
                    "sector_id": it.get("sector_id"),
                    "country_id": it.get("country_id"),
                    "market_id": it.get("market_id"),
                    "branch_id": it.get("branch_id"),
                    "stock_price_currency": it.get("stock_price_currency"),
                    "report_currency": it.get("report_currency"),
                }))
            except Exception:
                continue
    return out

def match_name_to_ticker(bd: BorsdataClient, company_query: str) -> Tuple[str, str]:
    items = _iter_instruments(bd)
    if not items:
        raise RuntimeError("Instrumentuniversum saknas i BorsdataClient.")

    q_raw = clean_query(company_query).strip()
    q = _clean_name(q_raw)
    by_ticker = { (it.ticker or "").upper(): it for it in items if it.ticker }

    # 0) Om query ser ut som en ticker (kort, inga mellanslag) → kontrollera TICKER först
    if re.fullmatch(r"[A-Z0-9.\-]{1,6}", q):
        if q in by_ticker:
            it = by_ticker[q]
            return (it.ticker.upper(), it.name)

    # 1) Exakt namn
    name_index = { _clean_name(it.name): it for it in items if it.name }
    if q in name_index:
        it = name_index[q]
        return (it.ticker.upper(), it.name)

    # 2) Prefix på namn
    prefix = [it for it in items if it.name and _clean_name(it.name).startswith(q)]
    if prefix:
        prefix.sort(key=lambda x: (0 if str(x.ticker).upper().endswith("B") else 1, x.ticker))
        return (prefix[0].ticker.upper(), prefix[0].name)

    # 3) Fuzzy på namn
    from difflib import get_close_matches
    candidates = get_close_matches(q, list(name_index.keys()), n=3, cutoff=0.6)
    if candidates:
        picks = [name_index[c] for c in candidates]
        picks.sort(key=lambda x: (0 if str(x.ticker).upper().endswith("B") else 1, x.ticker))
        return (picks[0].ticker.upper(), picks[0].name)

    # 4) Sista utväg: "contains" på namn (kan ge falska träffar som *Clean Motion* för "LEA")
    contains = [it for it in items if it.name and q in _clean_name(it.name)]
    if contains:
        contains.sort(key=lambda x: (0 if str(x.ticker).upper().endswith("B") else 1, x.ticker))
        return (contains[0].ticker.upper(), contains[0].name)

    # 5) Direkt ticker (om punkt 0 inte slog)
    if q in by_ticker:
        it = by_ticker[q]
        return (it.ticker.upper(), it.name)

    raise ValueError(f"Hittade inget instrument vars namn/ticker matchar '{company_query}'.")
